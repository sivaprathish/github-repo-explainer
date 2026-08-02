from __future__ import annotations

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def retrieve_documents(
    vector_store: FAISS,
    question: str,
    limit: int = 3,
) -> list[Document]:
    if not question.strip():
        return []

    return vector_store.similarity_search(
        question,
        k=limit,
    )