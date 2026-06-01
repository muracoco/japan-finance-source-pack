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


def jquants_daily_quotes(code: str, date: str) -> tuple[list[dict], list[dict], list[str]]:
    key = _api_key()
    if not key:
        return [], [], ["JQUANTS_API_KEY is not set; daily-quotes retrieval was skipped."]

    url = make_url(f"{BASE_URL}/prices/daily_quotes", {"code": code, "date": _format_date(date)})
    rows = _rows_from_jquants(url, key, "daily_quotes")
    limitations = [] if rows else ["J-Quants daily quotes returned no rows for this code/date."]
    return (
        [
            source(
                source_name="J-Quants daily quotes",
                source_type="jquants_daily_quotes",
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


def jquants_financial_statements(code: str) -> tuple[list[dict], list[dict], list[str]]:
    key = _api_key()
    if not key:
        return [], [], ["JQUANTS_API_KEY is not set; financial-statements retrieval was skipped."]

    url = make_url(f"{BASE_URL}/fins/statements", {"code": code})
    rows = _rows_from_jquants(url, key, "statements")
    limitations = [] if rows else ["J-Quants financial statements returned no rows for this code."]
    return (
        [
            source(
                source_name="J-Quants financial statements",
                source_type="jquants_financial_statements",
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


def _rows_from_jquants(url: str, key: str, preferred_key: str) -> list[dict]:
    payload = http_json(url, headers={"x-api-key": key})
    rows = payload.get(preferred_key) or payload.get("data") or payload.get("info") or []
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _format_date(value: str) -> str:
    if len(value) == 8 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return value
