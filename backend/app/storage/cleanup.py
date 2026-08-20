from pathlib import Path

from .metadata import (
    METADATA_DIR,
    is_expired,
    load_metadata,
)
from .qdrant import delete_document


def cleanup_expired_documents() -> None:
    """
    Remove expired documents from local storage
    and Qdrant Cloud.
    """

    if not METADATA_DIR.exists():
        return

    for metadata_file in METADATA_DIR.glob(
        "*.json"
    ):

        document_id = metadata_file.stem

        metadata = load_metadata(
            document_id
        )

        if metadata is None:
            continue

        if not is_expired(metadata):
            continue

        print(
            f"Cleaning expired document "
            f"{document_id[:12]}..."
        )

        # Delete vectors from Qdrant.
        try:

            delete_document(
                document_id
            )

            print(
                "Deleted document vectors "
                "from Qdrant."
            )

        except Exception as error:

            print(
                "Warning: could not delete "
                f"Qdrant vectors: {error}"
            )

        # Delete local PDF.
        file_path = Path(
            metadata["file_path"]
        )

        if file_path.exists():

            try:

                file_path.unlink()

                print(
                    f"Deleted local file: "
                    f"{file_path}"
                )

            except Exception as error:

                print(
                    "Warning: could not delete "
                    f"local file: {error}"
                )

        # Delete metadata.
        try:

            metadata_file.unlink()

            print(
                "Deleted document metadata."
            )

        except Exception as error:

            print(
                "Warning: could not delete "
                f"metadata: {error}"
            )