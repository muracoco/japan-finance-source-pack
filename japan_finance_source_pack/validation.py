from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "stock",
    "retrieved_sources",
    "extracted_facts",
    "chatgpt_required_fields",
    "limitations",
}

REQUIRED_STOCK_KEYS = {"code", "name", "market", "analysis_date"}
REQUIRED_SOURCE_KEYS = {
    "source_name",
    "source_type",
    "source_url",
    "retrieved_at",
    "is_primary_source",
    "data_delay_note",
    "limitations",
}


def validate_pack(pack: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    missing = sorted(REQUIRED_TOP_LEVEL_KEYS - set(pack))
    for key in missing:
        errors.append(f"missing top-level key: {key}")

    schema_version = pack.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version.strip():
        errors.append("schema_version must be a non-empty string")

    stock = pack.get("stock")
    if not isinstance(stock, Mapping):
        errors.append("stock must be an object")
    else:
        for key in sorted(REQUIRED_STOCK_KEYS):
            value = stock.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"stock.{key} must be a non-empty string")

    _validate_object_of_lists(pack, "retrieved_sources", errors)
    _validate_object_of_lists(pack, "extracted_facts", errors)

    retrieved_sources = pack.get("retrieved_sources")
    if isinstance(retrieved_sources, Mapping):
        for group_name, items in retrieved_sources.items():
            if not isinstance(items, list):
                continue
            for index, item in enumerate(items):
                _validate_source(item, f"retrieved_sources.{group_name}[{index}]", errors)

    chatgpt_required_fields = pack.get("chatgpt_required_fields")
    if not isinstance(chatgpt_required_fields, list) or not all(
        isinstance(item, str) and item.strip() for item in chatgpt_required_fields
    ):
        errors.append("chatgpt_required_fields must be a list of non-empty strings")

    limitations = pack.get("limitations")
    if not isinstance(limitations, list) or not all(isinstance(item, str) for item in limitations):
        errors.append("limitations must be a list of strings")

    return errors


def _validate_object_of_lists(pack: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = pack.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object")
        return
    for group_name, items in value.items():
        if not isinstance(group_name, str) or not group_name:
            errors.append(f"{key} contains an empty group name")
        if not isinstance(items, list):
            errors.append(f"{key}.{group_name} must be a list")


def _validate_source(item: Any, path: str, errors: list[str]) -> None:
    if not isinstance(item, Mapping):
        errors.append(f"{path} must be an object")
        return

    for key in sorted(REQUIRED_SOURCE_KEYS):
        if key not in item:
            errors.append(f"{path}.{key} is required")

    if "limitations" in item and not isinstance(item["limitations"], list):
        errors.append(f"{path}.limitations must be a list")
