from __future__ import annotations

import os

from .common import http_json, make_url, source

BASE_URL = "https://api.jquants.com/v2"
DELAY_NOTE = "J-Quants Free data can be delayed and plan-limited. Verify before using as latest market evidence."


def _api_key() -> str | None:
    return os.environ.get("JQUANTS_API_KEY") or os.environ.get("JQUANTS_ID_TOKEN")


def jquants_listed_info(code: str) -> tuple[list[dict], list[dict], list[str]]:
    key = _api_key()
    if not key:
        return [], [], ["JQUANTS_API_KEY is not set; listed-info retrieval was skipped."]

    url = make_url(f"{BASE_URL}/listed/info", {"code": code})
    payload = http_json(url, headers={"x-api-key": key})
    rows = payload.get("info") or payload.get("data") or []
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list):
        rows = []

    return (
        [
            source(
                source_name="J-Quants listed info",
                source_type="jquants_listed_info",
                source_url=url,
                is_primary_source=False,
                data_delay_note=DELAY_NOTE,
                limitations=[],
                row_count=len(rows),
            )
        ],
        rows,
        [],
    )
