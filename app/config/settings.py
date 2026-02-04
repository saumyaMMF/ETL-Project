"""Configuration settings for the ETL Dash application."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    aws_region: str = "eu-central-1"
    s3_bucket: str = "erp-genai-poc"
    s3_prefix: str = ""

    inputs_prefix: str = "inputs/raw"
    outputs_prefix: str = "outputs"
    logs_prefix: str = "logs"
    system_errors_prefix: str = "system/errors"

    house: str = "GUESS"
    collection_category: str = "GUESS APPAREL"
    basic_supplier_code: str = "1-2273"
    pricelist_season: str = "261"
    collection_code: str = "BSC"
    date_1: str = "1/12"
    date_2: str = "3/1"
    date_3: str = "27/4"

    lifecycle_days: int = 30


CONFIG = AppConfig()
