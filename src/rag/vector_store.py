from __future__ import annotations

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.rag.embeddings import get_embeddings


MAX_EMBEDDING_CHARACTERS = 350


def build_vector_store(
    documents: list[Document],
) -> FAISS:
    if not documents:
        raise ValueError(
            "No repository documents are available for indexing."
        )

    safe_documents: list[Document] = []

    for document in documents:
        content = document.page_content.strip()

        if not content:
            continue

        if len(content) > MAX_EMBEDDING_CHARACTERS:
            raise ValueError(
                "Oversized embedding chunk detected: "
                f"{len(content)} characters in "
                f"{document.metadata.get('file_path', 'unknown')}."
            )

        safe_documents.append(
            Document(
                page_content=content,
                metadata=document.metadata.copy(),
            )
        )

    if not safe_documents:
        raise ValueError(
            "No valid repository chunks remain after filtering."
        )

    print(
        "Embedding chunks:",
        len(safe_documents),
    )

    print(
        "Largest chunk characters:",
        max(
            len(document.page_content)
            for document in safe_documents
        ),
    )

    return FAISS.from_documents(
        documents=safe_documents,
        embedding=get_embeddings(),
    )