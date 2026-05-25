from __future__ import annotations

import os
from pathlib import Path


def _resolve_data_root() -> Path:
    """Use /tmp on read-only serverless (e.g. mistaken Vercel Python deploy)."""
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return Path("/tmp/editorial-engine-data")
    return Path(__file__).resolve().parent.parent.parent / "data"


DATA_ROOT = _resolve_data_root()

CHUNKS_DIR = DATA_ROOT / "chunks"
VOICES_DIR = DATA_ROOT / "voices"
DISCOVERY_DIR = DATA_ROOT / "discovery"
LAUNCH_QUEUE_DIR = DATA_ROOT / "launch_queue"
MEMORY_DIR = DATA_ROOT / "memory"
UPLOADS_DIR = DATA_ROOT / "uploads"


def ensure_data_dirs() -> None:
    for path in (
        CHUNKS_DIR,
        VOICES_DIR,
        DISCOVERY_DIR,
        LAUNCH_QUEUE_DIR,
        MEMORY_DIR,
        UPLOADS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
