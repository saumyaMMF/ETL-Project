"""AI agent logging with prompt hashing and validation results."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from app.logging.s3_logger import S3Logger
from app.utils.hash_utils import stable_hash


@dataclass
class AILog:
    file_id: str
    agent_name: str
    model_name: str
    prompt: Dict[str, Any]
    input_snapshot: Dict[str, Any]
    output: Dict[str, Any]
    confidence: float
    validation_result: str

    def to_payload(self) -> Dict[str, Any]:
        prompt_hash = stable_hash(self.prompt)
        return {
            "agent_name": self.agent_name,
            "model_name": self.model_name,
            "prompt_hash": prompt_hash,
            "prompt": self.prompt,
            "input_snapshot": self.input_snapshot,
            "output_json": self.output,
            "confidence": self.confidence,
            "validation_result": self.validation_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class AILogger:
    def __init__(self, s3_logger: S3Logger | None = None) -> None:
        self.s3_logger = s3_logger or S3Logger()

    def write(self, log: AILog) -> None:
        key = f"ai/{log.file_id}/{log.agent_name}.json"
        self.s3_logger.write(key, log.to_payload())
