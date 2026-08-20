from google import genai

from backend.app.core.config import (
    GENERATION_MODEL,
    GEMINI_API_KEY,
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def analyze_query(
    question: str,
) -> dict:
    """
    Analyze a user's question and produce
    a generic search representation.

    This does not assume anything about the
    document's domain.
    """

    prompt = f"""
You are the query analysis component of GyaanAI.

GyaanAI is a generic document question-answering
system. Documents can be of any type, including
books, research papers, resumes, contracts,
policies, manuals, reports, notes, or other documents.

Analyze this user question:

{question}

Return EXACTLY these three lines:

SEARCH_QUERY: <a concise semantic search query>
KEYWORDS: <keyword1>, <keyword2>, <keyword3>
INTENT: <brief description of what the user wants>

Rules:

- Preserve the meaning of the user's question.
- Do not assume the document's domain.
- Extract meaningful content words.
- Do not invent facts about the document.
- Keep the search query concise.
- Use up to 5 keywords.
- The intent should describe the user's information need.
"""

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )

    text = response.text.strip()

    search_query = question
    keywords = []
    intent = (
        "Answer the user's question "
        "using the document."
    )

    for line in text.splitlines():

        line = line.strip()

        if line.startswith(
            "SEARCH_QUERY:"
        ):

            search_query = (
                line[
                    len("SEARCH_QUERY:"):
                ].strip()
            )

        elif line.startswith(
            "KEYWORDS:"
        ):

            keyword_text = (
                line[
                    len("KEYWORDS:"):
                ].strip()
            )

            keywords = [
                keyword.strip()
                for keyword in (
                    keyword_text.split(",")
                )
                if keyword.strip()
            ]

        elif line.startswith(
            "INTENT:"
        ):

            intent = (
                line[
                    len("INTENT:"):
                ].strip()
            )

    return {
        "search_query": search_query,
        "keywords": keywords,
        "intent": intent,
    }