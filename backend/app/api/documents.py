import shutil
import uuid

from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from pydantic import BaseModel

from backend.app.documents.chunker import (
    create_chunks,
)

from backend.app.documents.loader import (
    extract_pdf_pages,
)

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
    METADATA_DIR,
    create_document_metadata,
    find_existing_document,
    load_metadata,
    save_metadata,
)

from backend.app.storage.qdrant import (
    save_documents,
)

from evaluation.service import (
    evaluate_response,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# ============================================================
# STORAGE
# ============================================================

UPLOAD_DIR = Path(
    "data/documents"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# MODELS
# ============================================================

class AskRequest(BaseModel):
    question: str


class SourceResponse(BaseModel):
    chunk_id: str
    page: int
    score: float
    text: str


class MetricsResponse(BaseModel):
    faithfulness: float | None
    answer_relevancy: float | None
    context_precision: float | None


class AskResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    sources: list[SourceResponse]
    metrics: MetricsResponse


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    expires_at: str


# ============================================================
# INGEST DOCUMENT
# ============================================================

def ingest_document(
    file_path: Path,
    filename: str,
):

    metadata = create_document_metadata(
        file_path
    )

    # Preserve original filename.
    metadata["filename"] = filename

    pages = extract_pdf_pages(
        file_path
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
                "document_id":
                    metadata[
                        "document_id"
                    ],

                "document_hash":
                    metadata[
                        "document_hash"
                    ],

                "chunk_id":
                    chunk.chunk_id,

                "page_number":
                    chunk.page_number,

                "text":
                    chunk.text,

                "expires_at":
                    metadata[
                        "expires_at"
                    ],
            }
        )

    # ========================================================
    # EMBEDDINGS
    # ========================================================

    for document in documents:

        document["embedding"] = (
            create_embedding(
                document["text"]
            )
        )

    # ========================================================
    # VECTOR STORAGE
    # ========================================================

    save_documents(
        documents
    )

    # ========================================================
    # METADATA STORAGE
    # ========================================================

    save_metadata(
        metadata
    )

    return metadata


# ============================================================
# LOAD CHUNKS
# ============================================================

def load_document_chunks(
    file_path: Path,
    metadata: dict,
):

    pages = extract_pdf_pages(
        file_path
    )

    chunks = create_chunks(
        pages,
        chunk_size=1000,
        overlap=150,
    )

    return [
        {
            "document_id":
                metadata[
                    "document_id"
                ],

            "chunk_id":
                chunk.chunk_id,

            "page_number":
                chunk.page_number,

            "text":
                chunk.text,
        }

        for chunk in chunks
    ]


# ============================================================
# LIST ACTIVE DOCUMENTS
# ============================================================

@router.get(
    "",
    response_model=list[
        DocumentResponse
    ],
)
def list_documents():

    # Remove expired documents first.
    cleanup_expired_documents()

    documents = []

    for metadata_file in (
        METADATA_DIR.glob(
            "*.json"
        )
    ):

        try:

            metadata = load_metadata(
                metadata_file.stem
            )

            if not metadata:
                continue

            document_id = metadata.get(
                "document_id"
            )

            if not document_id:
                continue

            # ------------------------------------------------
            # Original filename
            # ------------------------------------------------

            filename = metadata.get(
                "filename"
            )

            # Fallback for old metadata.
            if not filename:

                file_path = metadata.get(
                    "file_path"
                )

                if file_path:

                    filename = Path(
                        file_path
                    ).name

                else:

                    filename = (
                        f"{document_id}.pdf"
                    )

            documents.append(
                {
                    "document_id":
                        document_id,

                    "filename":
                        filename,

                    "expires_at":
                        metadata[
                            "expires_at"
                        ],
                }
            )

        except Exception as error:

            print(
                "Could not load metadata "
                f"{metadata_file}: {error}"
            )

    # Newest first.
    documents.sort(
        key=lambda document:
            document[
                "expires_at"
            ],
        reverse=True,
    )

    return documents


# ============================================================
# UPLOAD
# ============================================================

@router.post(
    "/upload"
)
async def upload_document(
    file: UploadFile = File(...),
):

    cleanup_expired_documents()

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    original_filename = (
        file.filename
    )

    # ========================================================
    # TEMPORARY DISK NAME
    # ========================================================

    temporary_name = (
        f"{uuid.uuid4().hex}.pdf"
    )

    file_path = (
        UPLOAD_DIR
        / temporary_name
    )

    # ========================================================
    # SAVE FILE
    # ========================================================

    with file_path.open(
        "wb"
    ) as destination:

        shutil.copyfileobj(
            file.file,
            destination,
        )

    try:

        # ====================================================
        # DUPLICATE CHECK
        # ====================================================

        existing = (
            find_existing_document(
                file_path
            )
        )

        if existing:

            file_path.unlink(
                missing_ok=True
            )

            existing_filename = (
                existing.get(
                    "filename"
                )
            )

            if not existing_filename:

                existing_file_path = (
                    existing.get(
                        "file_path"
                    )
                )

                if existing_file_path:

                    existing_filename = (
                        Path(
                            existing_file_path
                        ).name
                    )

                else:

                    existing_filename = (
                        original_filename
                    )

            return {
                "status":
                    "already_indexed",

                "document_id":
                    existing[
                        "document_id"
                    ],

                "filename":
                    existing_filename,

                "expires_at":
                    existing[
                        "expires_at"
                    ],
            }

        # ====================================================
        # INGEST
        # ====================================================

        metadata = ingest_document(
            file_path=file_path,
            filename=original_filename,
        )

        return {
            "status":
                "indexed",

            "document_id":
                metadata[
                    "document_id"
                ],

            "filename":
                metadata[
                    "filename"
                ],

            "expires_at":
                metadata[
                    "expires_at"
                ],
        }

    except HTTPException:

        file_path.unlink(
            missing_ok=True
        )

        raise

    except Exception as error:

        file_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# ASK DOCUMENT
# ============================================================

@router.post(
    "/{document_id}/ask",
    response_model=AskResponse,
)
def ask_document(
    document_id: str,
    request: AskRequest,
):

    cleanup_expired_documents()

    question = (
        request.question.strip()
    )

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    # ========================================================
    # LOAD METADATA
    # ========================================================

    metadata = None

    for metadata_file in (
        METADATA_DIR.glob(
            "*.json"
        )
    ):

        if metadata_file.stem == document_id:

            metadata = load_metadata(
                document_id
            )

            break

    if metadata is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found or expired.",
        )

    # ========================================================
    # VERIFY FILE
    # ========================================================

    file_path = Path(
        metadata["file_path"]
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document file is no longer available.",
        )

    # ========================================================
    # QUERY UNDERSTANDING
    # ========================================================

    query_analysis = analyze_query(
        question
    )

    semantic_query = (
        query_analysis.get(
            "search_query"
        )
        or question
    )

    # ========================================================
    # SEMANTIC RETRIEVAL
    # ========================================================

    query_embedding = create_embedding(
        semantic_query
    )

    semantic_results = (
        rank_documents(
            query_vector=query_embedding,
            document_id=document_id,
            top_k=10,
        )
    )

    # ========================================================
    # KEYWORD RETRIEVAL
    # ========================================================

    documents = load_document_chunks(
        file_path=file_path,
        metadata=metadata,
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
            top_k=10,
        )
    )

    # ========================================================
    # HYBRID RETRIEVAL
    # ========================================================

    hybrid_results = (
        reciprocal_rank_fusion(
            result_lists=[
                semantic_results,
                keyword_results,
            ],
            top_k=8,
        )
    )

    # ========================================================
    # GENERATION
    # ========================================================

    answer = generate_answer(
        question=question,
        results=hybrid_results,
    )

    # ========================================================
    # EVALUATION
    # ========================================================

    contexts = [
        result.text
        for result in hybrid_results
        if result.text
    ]

    metrics = evaluate_response(
        question=question,
        answer=answer,
        contexts=contexts,
    )

    # ========================================================
    # SOURCES
    # ========================================================

    sources = []

    for result in hybrid_results:

        sources.append(
            {
                "chunk_id":
                    result.chunk_id,

                "page":
                    result.page_number,

                "score":
                    float(
                        result.score
                    ),

                "text":
                    result.text,
            }
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "document_id":
            document_id,

        "question":
            question,

        "answer":
            answer,

        "sources":
            sources,

        "metrics":
            metrics,
    }