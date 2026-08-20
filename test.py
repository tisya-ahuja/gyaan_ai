import sys
from pathlib import Path


sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent
        / "backend"
    ),
)


from backend.app.documents.loader import extract_pdf_pages
from backend.app.documents.chunker import create_chunks

from backend.app.embeddings.service import (
    create_embedding,
)

from backend.app.generation.service import (
    generate_answer,
)

from backend.app.query.analyzer import (
    analyze_query,
)

from backend.app.retrieval.hybrid import (
    reciprocal_rank_fusion,
)

from backend.app.retrieval.keyword import (
    rank_documents_keyword,
)

from backend.app.retrieval.semantic import (
    rank_documents,
)

from backend.app.storage.cleanup import (
    cleanup_expired_documents,
)

from backend.app.storage.metadata import (
    create_document_metadata,
    find_existing_document,
    save_metadata,
)

from backend.app.storage.qdrant import (
    save_documents,
)

PDF_PATH = Path(
    "data/documents/sample.pdf"
)

def load_current_document(
    metadata,
):

    pages = extract_pdf_pages(
        Path(
            metadata["file_path"]
        )
    )

    chunks = create_chunks(
        pages,
        chunk_size=1000,
        overlap=150,
    )

    documents = []

    for chunk in chunks:

        documents.append(
            {
                "document_id": metadata[
                    "document_id"
                ],
                "document_hash": metadata[
                    "document_hash"
                ],
                "chunk_id": chunk.chunk_id,
                "page_number": chunk.page_number,
                "text": chunk.text,
                "expires_at": metadata[
                    "expires_at"
                ],
            }
        )

    return documents


def build_document_index():

    print(
        "\nChecking document..."
    )

    existing_metadata = (
        find_existing_document(
            PDF_PATH
        )
    )

    if existing_metadata:

        print(
            "Document already indexed."
        )

        print(
            f"Document ID: "
            f"{existing_metadata['document_id'][:12]}..."
        )

        return load_current_document(
            existing_metadata
        )

    print(
        "New or changed document detected."
    )

    print(
        "Existing embeddings will not be reused."
    )

    print(
        "\nLoading PDF..."
    )

    pages = extract_pdf_pages(
        PDF_PATH
    )

    print(
        f"Extracted {len(pages)} pages."
    )

    print(
        "\nCreating chunks..."
    )

    chunks = create_chunks(
        pages,
        chunk_size=1000,
        overlap=150,
    )

    print(
        f"Created {len(chunks)} chunks."
    )

    metadata = (
        create_document_metadata(
            PDF_PATH
        )
    )

    documents = []

    for chunk in chunks:

        documents.append(
            {
                "document_id": metadata[
                    "document_id"
                ],
                "document_hash": metadata[
                    "document_hash"
                ],
                "chunk_id": chunk.chunk_id,
                "page_number": chunk.page_number,
                "text": chunk.text,
                "expires_at": metadata[
                    "expires_at"
                ],
            }
        )

    print(
        "\nCreating embeddings..."
    )

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print(
            f"Embedding chunk "
            f"{index}/{len(documents)}"
        )

        document["embedding"] = (
            create_embedding(
                document["text"]
            )
        )

    print(
        "\nUploading embeddings "
        "to Qdrant Cloud..."
    )

    save_documents(
        documents
    )

    save_metadata(
        metadata
    )

    print(
        "Embeddings stored successfully."
    )

    return documents


def main():

    print("=" * 70)
    print("GYAANAI SYSTEM TEST")
    print("=" * 70)

    print(
        "\nCleaning expired documents..."
    )

    cleanup_expired_documents()
    # ------------------------------------------
    # Document ingestion / loading
    # ------------------------------------------

    documents = (
        build_document_index()
    )

    # ------------------------------------------
    # User question
    # ------------------------------------------

    question = input(
        "\nAsk a question about "
        "the document: "
    ).strip()

    if not question:

        print(
            "No question provided."
        )

        return

    print(
        f"\nQuestion: {question}"
    )

    # ------------------------------------------
    # Query understanding
    # ------------------------------------------

    print(
        "\nAnalyzing question..."
    )

    query_analysis = analyze_query(
        question
    )

    print(
        "\nQuery analysis:"
    )

    print(
        f"Search query: "
        f"{query_analysis.get('search_query')}"
    )

    print(
        f"Keywords: "
        f"{query_analysis.get('keywords')}"
    )

    print(
        f"Intent: "
        f"{query_analysis.get('intent')}"
    )

    # ------------------------------------------
    # Semantic retrieval
    # ------------------------------------------

    print(
        "\nRunning semantic retrieval..."
    )

    semantic_query = (
        query_analysis.get(
            "search_query"
        )
        or question
    )

    query_embedding = (
        create_embedding(
            semantic_query
        )
    )

    semantic_results = rank_documents(
        query_vector=query_embedding,
        document_id=documents[0]["document_id"],
        top_k=20,
    )

    # ------------------------------------------
    # Keyword retrieval
    # ------------------------------------------

    print(
        "Running keyword retrieval..."
    )

    keywords = query_analysis.get(
        "keywords",
        [],
    )

    keyword_query = " ".join(
        keywords
    )

    if not keyword_query:
        keyword_query = question

    keyword_results = (
        rank_documents_keyword(
            query=keyword_query,
            documents=documents,
            top_k=20,
        )
    )

    # ------------------------------------------
    # Hybrid retrieval
    # ------------------------------------------

    print(
        "Running hybrid retrieval..."
    )

    hybrid_results = (
        reciprocal_rank_fusion(
            result_lists=[
                semantic_results,
                keyword_results,
            ],
            top_k=10,
        )
    )

    # ------------------------------------------
    # Show retrieved evidence
    # ------------------------------------------

    print("\n" + "#" * 70)
    print("# RETRIEVED EVIDENCE")
    print("#" * 70)

    for rank, result in enumerate(
        hybrid_results,
        start=1,
    ):

        print(
            f"\n[{rank}] "
            f"Page {result.page_number} "
            f"| Score {result.score:.6f}"
        )

        print(
            f"Chunk: {result.chunk_id}"
        )

        print(
            result.text[:5]
        )

    # ------------------------------------------
    # Generation
    # ------------------------------------------

    print(
        "\nGenerating grounded answer..."
    )

    answer = generate_answer(
        question=question,
        results=hybrid_results,
    )

    # ------------------------------------------
    # Final answer
    # ------------------------------------------

    
    print("\n" + "#" * 70)
    print("# GYAANAI ANSWER")
    print("#" * 70)

    print(
        f"\n{answer}"
    )


if __name__ == "__main__":
    main()