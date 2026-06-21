from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector

from backend.config import settings


def _get_vector_store() -> PGVector:
    return PGVector(
        connection=settings.DATABASE_URL,
        embeddings=HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL),
        collection_name="opsmind_docs",
    )


async def retrieve(query: str, k: int = 5) -> list[dict]:
    vs = _get_vector_store()
    docs = vs.similarity_search(query, k=k)
    return [{"content": d.page_content, "metadata": d.metadata} for d in docs]
