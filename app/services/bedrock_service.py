"""Bedrock integration for AI interpretation (JSON-only outputs)."""

import json
from typing import Any, Dict

import boto3

from app.config.settings import CONFIG


class BedrockService:
    def __init__(self, region: str = CONFIG.aws_region) -> None:
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def invoke_json_model(self, model_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload)
        response = self.client.invoke_model(
            modelId=model_id,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        raw = response["body"].read()
        return json.loads(raw)
