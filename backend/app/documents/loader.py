import fitz


def extract_pdf_pages(
    pdf_path,
) -> list[dict]:
    """
    Extract text page-by-page from a PDF.
    """

    document = fitz.open(
        pdf_path
    )

    pages = []

    for page_number, page in enumerate(
        document,
        start=1,
    ):

        text = page.get_text(
            "text"
        ).strip()

        if not text:
            continue

        pages.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    document.close()

    return pages