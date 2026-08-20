from dataclasses import dataclass


@dataclass
class RetrievalResult:
    chunk_id: str
    page_number: int
    text: str
    score: float
    retrieval_method: str