from __future__ import annotations

from src.agents.qa_agent import answer_question
from src.rag.chunker import chunk_documents
from src.rag.document_builder import build_documents
from src.rag.retriever import retrieve_documents
from src.rag.vector_store import build_vector_store


class ChatService:
    def __init__(
        self,
        repository_name: str,
        files,
    ) -> None:
        documents = build_documents(
            repository_name=repository_name,
            files=files,
        )

        chunks = chunk_documents(documents)

        if not chunks:
            raise ValueError(
                "No repository content was available for indexing."
            )

        sizes = [
            len(chunk.page_content)
            for chunk in chunks
        ]

        print(f"Source documents: {len(documents)}")
        print(f"Embedding chunks: {len(chunks)}")
        print(f"Largest chunk: {max(sizes)} characters")

        # Must receive chunks, not full documents.
        self.vector_store = build_vector_store(chunks)

    def ask(self, question: str) -> str:
        cleaned_question = question.strip()

        if not cleaned_question:
            return "Enter a repository question."

        # Protect query embedding input as well.
        if len(cleaned_question) > 300:
            cleaned_question = cleaned_question[:300]

        retrieved_documents = retrieve_documents(
            vector_store=self.vector_store,
            question=cleaned_question,
            limit=3,
        )

        if not retrieved_documents:
            return (
                "I could not find relevant repository content "
                "for that question."
            )

        context_parts: list[str] = []

        for document in retrieved_documents:
            file_path = document.metadata.get(
                "file_path",
                "unknown",
            )

            context_parts.append(
                f"FILE: {file_path}\n"
                f"{document.page_content}"
            )

        # This limit affects the chat model prompt, not embeddings.
        context = "\n\n".join(context_parts)[:2500]

        return answer_question(
            question=cleaned_question,
            context=context,
        )