from dataclasses import dataclass

from backend.app.storage.qdrant import search_documents


@dataclass
class RetrievalResult:

    chunk_id: str
    page_number: int
    text: str
    score: float
    method: str = "semantic"


def rank_documents(
    query_vector: list[float],
    document_id: str,
    top_k: int = 10,
) -> list[RetrievalResult]:

    results = search_documents(
        query_vector=query_vector,
        document_id=document_id,
        top_k=top_k,
    )

    return [
        RetrievalResult(
            chunk_id=result["chunk_id"],
            page_number=result["page_number"],
            text=result["text"],
            score=float(
                result["score"]
            ),
            method="semantic",
        )
        for result in results
    ]