from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.base import get_llm


def answer_question(
    question: str,
    context: str,
) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
Answer questions about the repository using only the supplied
source-code context.

Mention relevant file paths in the answer.
If the answer is not present, say that it was not found.
""",
            ),
            (
                "human",
                """
Question:
{question}

Repository source context:
{context}
""",
            ),
        ]
    )

    chain = prompt | get_llm() | StrOutputParser()

    return chain.invoke(
        {
            "question": question,
            "context": context,
        },
        config={
            "run_name": "repository-qa-agent",
            "tags": ["github-explainer", "qa"],
        },
    )