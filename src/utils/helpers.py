import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def ensure_dir(directory: str | Path) -> Path:
    """Create directory (and parents) if it does not already exist."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_to_jsonl(data: dict[str, Any], filepath: str | Path) -> None:
    """Append a single record to a JSONL file (one JSON object per line)."""
    path = Path(filepath)
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def load_jsonl(filepath: str | Path) -> list[dict[str, Any]]:
    """Load all records from a JSONL file."""
    path = Path(filepath)
    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                logger.warning("Skipping malformed JSON at line %d: %s", line_num, exc)
    return records

def save_to_json(data: Any, filepath: str | Path, indent: int = 2) -> None:
    """Write any JSON-serialisable object to a pretty-printed JSON file."""
    path = Path(filepath)
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    logger.info("Saved JSON to %s", path)
