from backend.app.retrieval.models import RetrievalResult


def reciprocal_rank_fusion(
    result_lists: list[list[RetrievalResult]],
    top_k: int = 5,
    k: int = 60,
) -> list[RetrievalResult]:
    """
    Combine multiple ranked result lists using
    Reciprocal Rank Fusion (RRF).

    RRF score:

        1 / (k + rank)

    Results appearing highly in multiple retrieval
    methods receive stronger combined scores.
    """

    scores = {}

    result_lookup = {}

    for results in result_lists:

        for rank, result in enumerate(
            results,
            start=1,
        ):

            chunk_id = result.chunk_id

            rrf_score = 1 / (
                k + rank
            )

            scores[chunk_id] = (
                scores.get(chunk_id, 0.0)
                + rrf_score
            )

            result_lookup[chunk_id] = result

    ranked_chunk_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    final_results = []

    for chunk_id in ranked_chunk_ids[:top_k]:

        original_result = result_lookup[
            chunk_id
        ]

        final_results.append(
            RetrievalResult(
                chunk_id=original_result.chunk_id,
                page_number=original_result.page_number,
                text=original_result.text,
                score=scores[chunk_id],
                retrieval_method="hybrid",
            )
        )

    return final_results