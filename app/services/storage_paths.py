from __future__ import annotations

from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parent.parent.parent / "data"

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
