from __future__ import annotations

import io

from app.services.chunk_store import store_document
from app.services.storage_paths import UPLOADS_DIR, ensure_data_dirs


def parse_bytes(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return content.decode("utf-8", errors="replace")


def ingest_upload(filename: str, content: bytes) -> dict:
    import uuid

    ensure_data_dirs()
    file_id = str(uuid.uuid4())[:12]
    path = UPLOADS_DIR / f"{file_id}_{filename}"
    path.write_bytes(content)
    text = parse_bytes(filename, content)
    chunks = store_document(text=text, source_url=f"upload://{file_id}", source_title=filename)
    return {
        "file_id": file_id,
        "filename": filename,
        "chunk_count": len(chunks),
        "preview": text[:500],
        "chunks": chunks,
    }
