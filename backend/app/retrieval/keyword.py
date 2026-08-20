import math
import re
from collections import Counter

from backend.app.retrieval.models import RetrievalResult


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


def tokenize(
    text: str,
) -> list[str]:

    tokens = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower(),
    )

    return [
        token
        for token in tokens
        if token not in STOPWORDS
    ]


def calculate_idf(
    documents: list[dict],
) -> dict[str, float]:

    document_count = len(
        documents
    )

    document_frequency = Counter()

    for document in documents:

        tokens = set(
            tokenize(
                document["text"]
            )
        )

        for token in tokens:
            document_frequency[
                token
            ] += 1

    idf = {}

    for token, frequency in (
        document_frequency.items()
    ):

        idf[token] = math.log(
            (document_count + 1)
            / (frequency + 1)
        ) + 1

    return idf


def keyword_score(
    query_tokens: list[str],
    document: dict,
    idf: dict[str, float],
) -> float:

    document_tokens = tokenize(
        document["text"]
    )

    if not document_tokens:
        return 0.0

    term_frequency = Counter(
        document_tokens
    )

    score = 0.0

    for token in query_tokens:

        if token in term_frequency:

            frequency = (
                term_frequency[token]
                / len(document_tokens)
            )

            score += (
                frequency
                * idf.get(token, 0.0)
            )

    return score


def rank_documents_keyword(
    query: str,
    documents: list[dict],
    top_k: int = 5,
) -> list[RetrievalResult]:

    query_tokens = tokenize(
        query
    )

    idf = calculate_idf(
        documents
    )

    results = []

    for document in documents:

        score = keyword_score(
            query_tokens=query_tokens,
            document=document,
            idf=idf,
        )

        if score <= 0:
            continue

        results.append(
            RetrievalResult(
                chunk_id=document[
                    "chunk_id"
                ],
                page_number=document[
                    "page_number"
                ],
                text=document["text"],
                score=score,
                retrieval_method="keyword",
            )
        )

    results.sort(
        key=lambda result: result.score,
        reverse=True,
    )

    return results[:top_k]