from __future__ import annotations

from langchain_core.documents import Document

from src.models.analysis_models import RepositoryFile


def build_documents(
    repository_name: str,
    files: list[RepositoryFile],
) -> list[Document]:
    documents: list[Document] = []

    for file in files:
        content = file.content.strip()

        if not content:
            continue

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "repository": repository_name,
                    "file_path": file.path,
                    "extension": file.extension,
                    "line_count": file.line_count,
                },
            )
        )

    return documents