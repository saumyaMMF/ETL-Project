"""Generate signed URLs for uploads/downloads."""

from app.config.settings import CONFIG
from app.services.s3_service import S3Service


class SignedUrlService:
    def __init__(self, s3_service: S3Service | None = None) -> None:
        self.s3_service = s3_service or S3Service()

    def create_upload_url(self, file_id: str, filename: str, content_type: str) -> str:
        key = f"{CONFIG.inputs_prefix}/{file_id}/{filename}"
        return self.s3_service.generate_presigned_url(
            key=key,
            method="put_object",
            content_type=content_type,
        )

    def create_download_url(self, key: str) -> str:
        return self.s3_service.generate_presigned_url(
            key=key,
            method="get_object",
        )
