"""S3 client wrapper for reading/writing artifacts."""

import json
from typing import Any, Dict, Optional

import boto3

from app.config.settings import CONFIG


class S3Service:
    def __init__(self, bucket: str = CONFIG.s3_bucket, region: str = CONFIG.aws_region) -> None:
        self.bucket = bucket
        self.region = region
        self.client = boto3.client("s3", region_name=region)

    def put_bytes(self, key: str, data: bytes, content_type: str) -> None:
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    def put_json(self, key: str, payload: Dict[str, Any]) -> None:
        self.put_bytes(key, json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"), "application/json")

    def get_json(self, key: str) -> Dict[str, Any]:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        body = response["Body"].read()
        return json.loads(body.decode("utf-8"))

    def generate_presigned_url(
        self,
        key: str,
        method: str,
        expires_in: int = 900,
        content_type: Optional[str] = None,
    ) -> str:
        params: Dict[str, Any] = {"Bucket": self.bucket, "Key": key}
        if content_type:
            params["ContentType"] = content_type
        return self.client.generate_presigned_url(
            ClientMethod=method,
            Params=params,
            ExpiresIn=expires_in,
        )
