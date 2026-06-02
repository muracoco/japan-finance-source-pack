from __future__ import annotations

import os

from .common import http_json, source

BASE_URL = "https://edinetdb.jp/v1"
DELAY_NOTE = "EDINET DB aggregates public disclosure data. Verify source filing dates and attribution requirements."


def _api_key() -> str | None:
    return os.environ.get("EDINETDB_API_KEY")


def edinetdb_company_profile(code: str) -> tuple[list[dict], list[dict], list[str]]:
    key = _api_key()
    if not key:
        return [], [], ["EDINETDB_API_KEY is not set; EDINET DB lookup was skipped."]

    url = f"{BASE_URL}/companies/{code}"
    payload = http_json(url, headers={"X-API-Key": key})
    rows = _company_profile_rows(payload)

    limitations = []
    if not rows:
        limitations.append("EDINET DB returned no company profile data for this code.")

    return (
        [
            source(
                source_name="EDINET DB company profile",
                source_type="edinetdb_company_profile",
                source_url=url,
                is_primary_source=False,
                data_delay_note=DELAY_NOTE,
                limitations=limitations,
                row_count=len(rows),
            )
        ],
        rows,
        limitations,
    )


def _company_profile_rows(payload: dict) -> list[dict]:
    data = payload.get("data", payload)
    if isinstance(data, dict):
        return [data]
    return []
