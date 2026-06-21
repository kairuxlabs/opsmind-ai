import asyncio

import asyncpg
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector

from backend.config import settings


def _get_vector_store() -> PGVector:
    return PGVector(
        connection=settings.DATABASE_URL,
        embeddings=HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL),
        collection_name="opsmind_docs",
    )


_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder  # lazy — torch optional at import time
        _reranker = CrossEncoder(settings.RERANKER_MODEL)
    return _reranker


def _semantic_search(query: str, k: int) -> list[dict]:
    vs = _get_vector_store()
    docs = vs.similarity_search(query, k=k)
    return [{"content": d.page_content, "metadata": d.metadata} for d in docs]


async def _keyword_search(query: str, k: int) -> list[dict]:
    """Full-text search on the PGVector document store using PostgreSQL tsvector."""
    conn = await asyncpg.connect(settings.DATABASE_URL_ASYNC)
    try:
        rows = await conn.fetch(
            """
            SELECT e.document, e.cmetadata
            FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON e.collection_id = c.uuid
            WHERE c.name = 'opsmind_docs'
              AND to_tsvector('english', e.document) @@ plainto_tsquery('english', $1)
            ORDER BY ts_rank(to_tsvector('english', e.document), plainto_tsquery('english', $1)) DESC
            LIMIT $2
            """,
            query,
            k,
        )
        return [{"content": r["document"], "metadata": r["cmetadata"] or {}} for r in rows]
    finally:
        await conn.close()


def _reciprocal_rank_fusion(ranked_lists: list[list[dict]], top_k: int = 10, rrf_k: int = 60) -> list[dict]:
    """Merge multiple ranked doc lists via Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    docs_by_key: dict[str, dict] = {}

    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked):
            key = doc["content"][:200]  # dedup by content prefix
            scores[key] = scores.get(key, 0.0) + 1.0 / (rank + rrf_k)
            docs_by_key[key] = doc

    sorted_keys = sorted(scores, key=lambda k: scores[k], reverse=True)
    return [docs_by_key[k] for k in sorted_keys[:top_k]]


def _rerank(query: str, docs: list[dict], top_k: int) -> list[dict]:
    if not docs:
        return docs
    reranker = _get_reranker()
    pairs = [(query, d["content"]) for d in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in ranked[:top_k]]


async def retrieve(query: str, k: int = 5) -> list[dict]:
    """Hybrid retrieval: semantic + keyword search, merged via RRF, re-ranked by cross-encoder."""
    # Run semantic search in thread (LangChain is sync) and keyword search concurrently
    semantic_task = asyncio.to_thread(_semantic_search, query, 10)
    keyword_task = _keyword_search(query, 10)

    semantic_docs, keyword_docs = await asyncio.gather(
        semantic_task, keyword_task, return_exceptions=True
    )

    # Gracefully degrade if either source fails
    lists = []
    if isinstance(semantic_docs, list):
        lists.append(semantic_docs)
    if isinstance(keyword_docs, list):
        lists.append(keyword_docs)

    if not lists:
        return []

    merged = _reciprocal_rank_fusion(lists, top_k=10)
    return _rerank(query, merged, top_k=k)
