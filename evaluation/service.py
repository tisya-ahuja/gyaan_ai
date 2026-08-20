import json
import os
import re

from dotenv import load_dotenv
from google import genai


load_dotenv()


GENERATION_MODEL = "gemini-3.6-flash"


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def _empty_metrics() -> dict:
    return {
        "faithfulness": None,
        "answer_relevancy": None,
        "context_precision": None,
    }


def _extract_json(text: str) -> dict:
    """
    Extract JSON from a model response.

    Supports:
    - plain JSON
    - ```json ... ```
    - JSON surrounded by other text
    """

    if not text:
        raise ValueError(
            "Evaluator returned an empty response."
        )

    text = text.strip()

    # Remove markdown code fences.
    text = re.sub(
        r"```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```",
        "",
        text,
    )

    # First try the complete response.
    try:
        result = json.loads(text)

        if not isinstance(result, dict):
            raise ValueError(
                "Evaluator JSON is not an object."
            )

        return result

    except json.JSONDecodeError:
        pass

    # Otherwise find the first JSON object.
    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if not match:
        raise ValueError(
            "Could not find JSON in evaluator response."
        )

    result = json.loads(
        match.group(0)
    )

    if not isinstance(result, dict):
        raise ValueError(
            "Evaluator JSON is not an object."
        )

    return result


def _clamp_score(value):
    """
    Ensure scores remain between 0 and 1.
    """

    try:

        value = float(value)

        return round(
            max(
                0.0,
                min(
                    1.0,
                    value,
                ),
            ),
            4,
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


def evaluate_response(
    question: str,
    answer: str,
    contexts: list[str],
) -> dict:
    """
    Evaluate one RAG response.

    This is completely document-agnostic.

    Metrics:

    - faithfulness
    - answer_relevancy
    - context_precision
    """

    if not question:
        return _empty_metrics()

    if not answer:
        return _empty_metrics()

    if not contexts:
        return _empty_metrics()

    context_text = "\n\n".join(
        f"[Context {index + 1}]\n{context}"
        for index, context in enumerate(
            contexts
        )
    )

    prompt = f"""
You are evaluating a Retrieval-Augmented Generation (RAG) system.

Evaluate ONLY the relationship between:

1. The user's question
2. The retrieved document contexts
3. The generated answer

Do NOT use outside knowledge.

USER QUESTION:
{question}

RETRIEVED CONTEXTS:
{context_text}

GENERATED ANSWER:
{answer}

Evaluate the following metrics.

FAITHFULNESS:
How well is every factual claim in the answer supported
by the retrieved contexts?

0.0 = unsupported or contradicted
0.5 = partially supported
1.0 = completely supported

ANSWER RELEVANCY:
How directly does the answer address the user's question?

0.0 = does not answer the question
0.5 = partially answers the question
1.0 = directly and completely answers the question

CONTEXT PRECISION:
How relevant are the retrieved contexts to the user's question?

Consider the retrieved contexts as a group.

0.0 = mostly irrelevant
0.5 = mixed relevance
1.0 = highly relevant

IMPORTANT:

Judge only what is present in the retrieved contexts.

Do not reward the answer for information that comes
from outside the retrieved contexts.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "faithfulness": 0.0,
    "answer_relevancy": 0.0,
    "context_precision": 0.0
}}
"""

    try:

        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
        )

        result = _extract_json(
            response.text
        )

        metrics = {
            "faithfulness": _clamp_score(
                result.get(
                    "faithfulness"
                )
            ),
            "answer_relevancy": _clamp_score(
                result.get(
                    "answer_relevancy"
                )
            ),
            "context_precision": _clamp_score(
                result.get(
                    "context_precision"
                )
            ),
        }

        print(
            "\nRAG evaluation:"
        )

        print(
            f"Faithfulness: "
            f"{metrics['faithfulness']}"
        )

        print(
            f"Answer relevancy: "
            f"{metrics['answer_relevancy']}"
        )

        print(
            f"Context precision: "
            f"{metrics['context_precision']}"
        )

        return metrics

    except Exception as exc:

        print(
            "\nRAG evaluation failed:"
        )

        print(
            repr(exc)
        )

        return _empty_metrics()