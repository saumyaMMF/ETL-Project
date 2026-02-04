"""Hash utilities for prompt snapshots and deterministic logging."""

import hashlib
import json
from typing import Any, Dict


def stable_hash(payload: Dict[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
