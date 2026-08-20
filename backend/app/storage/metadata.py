import hashlib
import json

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from pathlib import Path
from typing import Any


METADATA_DIR = Path(
    "data/metadata"
)

METADATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# FILE HASH
# ============================================================

def calculate_file_hash(
    file_path: Path,
) -> str:

    sha256 = hashlib.sha256()

    with file_path.open(
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# ============================================================
# CREATE METADATA
# ============================================================

def create_document_metadata(
    file_path: Path,
) -> dict[str, Any]:

    document_hash = (
        calculate_file_hash(
            file_path
        )
    )

    now = datetime.now(
        timezone.utc
    )

    # ========================================================
    # DOCUMENT LIFETIME
    # ========================================================
    #
    # Documents remain active for 30 minutes.
    #

    expires_at = (
        now
        + timedelta(
            minutes=30
        )
    )

    return {
        "document_id":
            document_hash,

        "document_hash":
            document_hash,

        "filename":
            file_path.name,

        "file_path":
            str(file_path),

        "created_at":
            now.isoformat(),

        "expires_at":
            expires_at.isoformat(),
    }


# ============================================================
# METADATA PATH
# ============================================================

def metadata_path(
    document_id: str,
) -> Path:

    return (
        METADATA_DIR
        / f"{document_id}.json"
    )


# ============================================================
# SAVE
# ============================================================

def save_metadata(
    metadata: dict[str, Any],
) -> None:

    path = metadata_path(
        metadata["document_id"]
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
        )


# ============================================================
# LOAD
# ============================================================

def load_metadata(
    document_id: str,
) -> dict[str, Any] | None:

    path = metadata_path(
        document_id
    )

    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ============================================================
# EXPIRATION
# ============================================================

def is_expired(
    metadata: dict[str, Any],
) -> bool:

    expires_at = datetime.fromisoformat(
        metadata["expires_at"]
    )

    return (
        datetime.now(
            timezone.utc
        )
        >= expires_at
    )


# ============================================================
# FIND EXISTING DOCUMENT
# ============================================================

def find_existing_document(
    file_path: Path,
) -> dict[str, Any] | None:

    document_hash = (
        calculate_file_hash(
            file_path
        )
    )

    metadata = load_metadata(
        document_hash
    )

    if metadata is None:
        return None

    if is_expired(metadata):
        return None

    return metadata