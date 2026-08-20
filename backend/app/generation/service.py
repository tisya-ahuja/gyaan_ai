from google import genai

from backend.app.core.config import (
    GENERATION_MODEL,
    GEMINI_API_KEY,
)
from backend.app.retrieval.models import RetrievalResult


client = genai.Client(
    api_key=GEMINI_API_KEY
)


SYSTEM_INSTRUCTION = """
You are GyaanAI, a generic document
question-answering assistant.

Answer the user's question using ONLY
the supplied document context.

Rules:

1. Do not use outside knowledge.
2. Do not invent facts.
3. If the supplied context does not contain
   enough information, clearly say so.
4. Give a concise and useful answer.
5. Cite supporting pages using [Page X].
6. Do not cite a page unless the supplied
   context actually supports the claim.
7. If multiple pages support the answer,
   cite each relevant page.
"""


def build_context(
    results: list[RetrievalResult],
) -> str:

    context_parts = []

    for result in results:

        context_parts.append(
            (
                f"[Page {result.page_number} | "
                f"Chunk {result.chunk_id}]\n"
                f"{result.text}"
            )
        )

    return "\n\n".join(
        context_parts
    )


def generate_answer(
    question: str,
    results: list[RetrievalResult],
) -> str:

    context = build_context(
        results
    )

    prompt = f"""
{SYSTEM_INSTRUCTION}

DOCUMENT CONTEXT
================

{context}

USER QUESTION
=============

{question}

Now answer the user's question.
"""

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )

    return response.text.strip()