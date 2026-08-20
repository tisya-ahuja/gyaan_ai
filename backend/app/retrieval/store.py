import hashlib
import json
from pathlib import Path


STORE_PATH = Path(
    "data/vector_store.json"
)


def calculate_file_hash(
    file_path: Path,
) -> str:
    """
    Calculate a SHA-256 hash of the document.

    If even a small part of the document changes,
    the hash changes.
    """

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:

        while True:

            data = file.read(
                1024 * 1024
            )

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def save_documents(
    documents: list[dict],
    document_hash: str,
) -> None:

    STORE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    store = {
        "document_hash": document_hash,
        "documents": documents,
    }

    with STORE_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            store,
            file,
            ensure_ascii=False,
        )


def load_documents(
    document_hash: str,
) -> list[dict]:

    if not STORE_PATH.exists():
        return []

    with STORE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        store = json.load(file)

    stored_hash = store.get(
        "document_hash"
    )

    if stored_hash != document_hash:

        return []

    return store.get(
        "documents",
        [],
    )