"""Validation rules for AI mapping and ERP requirements."""

from typing import Dict, Iterable, List


REQUIRED_FIELDS = {
    "COLLECTION_ITEMS": ["supplier_item_code", "gender", "size_desc", "drop"],
    "COLLECTION_CHANGES": ["supplier_item_code", "color_code"],
    "ORDER_CONFIRMATIONS": ["supplier_item_code", "color_code", "size_desc", "quantity"],
}


def validate_mapping(file_type: str, mapping: Dict[str, str]) -> List[str]:
    errors: List[str] = []
    required = REQUIRED_FIELDS.get(file_type, [])
    for field in required:
        if field not in mapping or not mapping[field]:
            errors.append(f"Missing required field mapping: {field}")
    return errors


def validate_required_columns(
    columns: Iterable[str],
    required_columns: Iterable[str],
) -> List[str]:
    missing = [col for col in required_columns if col not in columns]
    return [f"Missing required column: {col}" for col in missing]
