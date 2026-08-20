from google import genai

from backend.app.core.config import (
    EMBEDDING_MODEL,
    GEMINI_API_KEY,
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def create_embedding(
    text: str,
) -> list[float]:

    response = (
        client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )
    )

    return list(
        response.embeddings[0].values
    )