import os

from dotenv import load_dotenv


load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Add it to the .env file."
    )


EMBEDDING_MODEL = (
    "gemini-embedding-001"
)

GENERATION_MODEL = (
    "gemini-3.6-flash"
)