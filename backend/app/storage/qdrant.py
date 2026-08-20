import os
import uuid
from typing import Any

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
    PayloadSchemaType,
)

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "gyaanai_documents"

VECTOR_SIZE = 3072


if not QDRANT_URL:
    raise RuntimeError("QDRANT_URL is missing from .env")

if not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_API_KEY is missing from .env")


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def ensure_collection() -> None:

    collections = client.get_collections()

    existing_names = {
        collection.name
        for collection in collections.collections
    }

    if COLLECTION_NAME not in existing_names:

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="document_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )

        return

    # Collection already exists.
    # Make sure the document_id index exists.
    collection_info = client.get_collection(
        COLLECTION_NAME
    )

    payload_schema = (
        collection_info.payload_schema
        or {}
    )

    if "document_id" not in payload_schema:

        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="document_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )


def save_documents(
    documents: list[dict[str, Any]],
) -> None:

    ensure_collection()

    points = []

    for document in documents:

        point_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                (
                    f"{document['document_id']}:"
                    f"{document['chunk_id']}"
                ),
            )
        )

        payload = {
            "document_id": document["document_id"],
            "document_hash": document["document_hash"],
            "chunk_id": document["chunk_id"],
            "page_number": document["page_number"],
            "text": document["text"],
            "expires_at": document["expires_at"],
        }

        points.append(
            PointStruct(
                id=point_id,
                vector=document["embedding"],
                payload=payload,
            )
        )

    if not points:
        return

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )


def delete_document(
    document_id: str,
) -> None:

    ensure_collection()

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(
                        value=document_id,
                    ),
                )
            ]
        ),
    )


def search_documents(
    query_vector: list[float],
    document_id: str,
    top_k: int = 10,
) -> list[dict[str, Any]]:

    ensure_collection()

    query_filter = Filter(
        must=[
            FieldCondition(
                key="document_id",
                match=MatchValue(
                    value=document_id,
                ),
            )
        ]
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    ).points

    formatted_results = []

    for result in results:

        payload = result.payload or {}

        formatted_results.append(
            {
                "chunk_id": payload.get(
                    "chunk_id"
                ),
                "page_number": payload.get(
                    "page_number"
                ),
                "text": payload.get(
                    "text",
                    "",
                ),
                "score": result.score,
                "document_id": payload.get(
                    "document_id"
                ),
            }
        )

    return formatted_results