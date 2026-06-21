from pathlib import Path

import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector

from backend.config import settings


def _chunk(text: str, size: int = 1000, overlap: int = 100) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)


def _get_vector_store() -> PGVector:
    return PGVector(
        connection=settings.DATABASE_URL,
        embeddings=_get_embeddings(),
        collection_name="opsmind_docs",
    )


async def ingest_csv(file_path: str) -> int:
    df = pd.read_csv(file_path)
    docs = []
    for i, row in df.iterrows():
        content = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
        docs.append(Document(page_content=content, metadata={"source": file_path, "row": i}))
    vs = _get_vector_store()
    vs.add_documents(docs)
    return len(docs)


async def ingest_text(file_path: str) -> int:
    content = Path(file_path).read_text(encoding="utf-8")
    docs = [Document(page_content=content, metadata={"source": file_path})]
    vs = _get_vector_store()
    vs.add_documents(docs)
    return len(docs)


async def ingest_pdf(file_path: str) -> int:
    import pdfplumber
    docs = []
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            if not text.strip():
                continue
            for chunk in _chunk(text):
                docs.append(Document(
                    page_content=chunk,
                    metadata={"source": file_path, "page": page_num},
                ))
    if not docs:
        return 0
    vs = _get_vector_store()
    vs.add_documents(docs)
    return len(docs)
