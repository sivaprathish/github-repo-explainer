from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


MAX_CHUNK_CHARACTERS = 350
CHUNK_OVERLAP = 30


def chunk_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Split repository content into small chunks that remain below
    the embedding model's 512-token input limit.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_CHARACTERS,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=[
            "\nclass ",
            "\ninterface ",
            "\ndef ",
            "\nasync def ",
            "\nfunction ",
            "\nexport ",
            "\n\n",
            "\n",
            " ",
            "",
        ],
    )

    initial_chunks = splitter.split_documents(documents)

    safe_chunks: list[Document] = []

    for chunk in initial_chunks:
        content = chunk.page_content.strip()

        if not content:
            continue

        # A final hard split guarantees no chunk exceeds 350 characters.
        if len(content) <= MAX_CHUNK_CHARACTERS:
            safe_chunks.append(chunk)
            continue

        step = MAX_CHUNK_CHARACTERS - CHUNK_OVERLAP

        for start in range(0, len(content), step):
            part = content[
                start : start + MAX_CHUNK_CHARACTERS
            ].strip()

            if not part:
                continue

            metadata = chunk.metadata.copy()
            metadata["subchunk_start"] = start

            safe_chunks.append(
                Document(
                    page_content=part,
                    metadata=metadata,
                )
            )

    return safe_chunks