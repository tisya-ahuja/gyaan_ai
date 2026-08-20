import re
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    chunk_id: str
    page_number: int
    text: str


def split_sentences(
    text: str,
) -> list[str]:

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def create_chunks(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[DocumentChunk]:

    chunks = []

    for page in pages:

        page_number = page[
            "page_number"
        ]

        text = page["text"]

        sentences = split_sentences(
            text
        )

        current = ""
        chunk_index = 0

        for sentence in sentences:

            if (
                len(current)
                + len(sentence)
                + 1
                <= chunk_size
            ):

                current = (
                    f"{current} "
                    f"{sentence}"
                ).strip()

            else:

                if current:

                    chunks.append(
                        DocumentChunk(
                            chunk_id=(
                                f"page-"
                                f"{page_number}-"
                                f"chunk-"
                                f"{chunk_index}"
                            ),
                            page_number=page_number,
                            text=current,
                        )
                    )

                    chunk_index += 1

                overlap_text = (
                    current[-overlap:]
                    if current
                    else ""
                )

                current = (
                    f"{overlap_text} "
                    f"{sentence}"
                ).strip()

        if current:

            chunks.append(
                DocumentChunk(
                    chunk_id=(
                        f"page-"
                        f"{page_number}-"
                        f"chunk-"
                        f"{chunk_index}"
                    ),
                    page_number=page_number,
                    text=current,
                )
            )

    return chunks