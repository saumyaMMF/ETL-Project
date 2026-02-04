"""File-level logging."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.logging.s3_logger import S3Logger


@dataclass
class FileLog:
    file_id: str
    original_filename: str
    detected_file_type: str | None = None
    upload_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    processing_status: str = "pending"
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    output_paths: List[str] = field(default_factory=list)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "file_id": self.file_id,
            "original_filename": self.original_filename,
            "detected_file_type": self.detected_file_type,
            "upload_timestamp": self.upload_timestamp,
            "processing_status": self.processing_status,
            "errors": self.errors,
            "warnings": self.warnings,
            "output_paths": self.output_paths,
        }


class FileLogger:
    def __init__(self, s3_logger: S3Logger | None = None) -> None:
        self.s3_logger = s3_logger or S3Logger()

    def write(self, log: FileLog) -> None:
        key = f"files/{log.file_id}.json"
        self.s3_logger.write(key, log.to_payload())
