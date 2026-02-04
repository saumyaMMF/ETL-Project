"""S3-backed logging utilities."""

from typing import Any, Dict

from app.config.settings import CONFIG
from app.services.s3_service import S3Service


class S3Logger:
    def __init__(self, s3_service: S3Service | None = None) -> None:
        self.s3_service = s3_service or S3Service()

    def write(self, key: str, payload: Dict[str, Any]) -> None:
        full_key = f"{CONFIG.logs_prefix}/{key}"
        self.s3_service.put_json(full_key, payload)
