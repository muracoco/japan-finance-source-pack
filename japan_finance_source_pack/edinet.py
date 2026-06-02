from __future__ import annotations

import os

from .common import http_json, make_url, source

BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"
DISCLOSURE_NOTE = "EDINET filing metadata is disclosure-date based. Verify document details before extracting facts."
TARGET_DOC_TYPES = {"120", "130", "140", "160"}
DOC_TYPE_LABELS = {
    "120": "annual_securities_report",
    "130": "quarterly_report",
    "140": "semiannual_report",
    "160": "amendment_report",
}


def _api_key() -> str | None:
    return os.environ.get("EDINET_API_KEY")


def edinet_document_metadata(date: str, sec_code: str) -> tuple[list[dict], list[dict], list[str]]:
    key = _api_key()
    if not key:
        return [], [], ["EDINET_API_KEY is not set; EDINET metadata discovery was skipped."]

    query = {"date": _format_date(date), "type": 2, "Subscription-Key": key}
    url = make_url(f"{BASE_URL}/documents.json", query)
    payload = http_json(url)
    rows = payload.get("results") or []
    if not isinstance(rows, list):
        rows = []

    normalized_code = _normalize_sec_code(sec_code)
    matching_rows = [
        _document_summary(row)
        for row in rows
        if isinstance(row, dict)
        and _normalize_sec_code(str(row.get("secCode") or "")) == normalized_code
        and str(row.get("docTypeCode") or "") in TARGET_DOC_TYPES
    ]

    limitations = []
    if not matching_rows:
        limitations.append("No EDINET annual, amendment, quarterly, or semiannual filings matched this security code/date.")

    return (
        [
            source(
                source_name="EDINET document metadata",
                source_type="edinet_document_metadata",
                source_url=_redact_subscription_key(url),
                is_primary_source=True,
                data_delay_note=DISCLOSURE_NOTE,
                limitations=limitations,
                row_count=len(matching_rows),
            )
        ],
        matching_rows,
        limitations,
    )


def _format_date(value: str) -> str:
    if len(value) == 8 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return value


def _normalize_sec_code(value: str) -> str:
    return value.strip()[:4]


def _document_summary(row: dict) -> dict:
    keys = [
        "docID",
        "edinetCode",
        "secCode",
        "filerName",
        "docTypeCode",
        "periodStart",
        "periodEnd",
        "submitDateTime",
        "docDescription",
        "xbrlFlag",
        "pdfFlag",
        "csvFlag",
    ]
    summary = {key: row.get(key) for key in keys if key in row}
    doc_type_code = str(row.get("docTypeCode") or "")
    if doc_type_code in DOC_TYPE_LABELS:
        summary["document_category"] = DOC_TYPE_LABELS[doc_type_code]
    return summary


def _redact_subscription_key(url: str) -> str:
    return url.split("&Subscription-Key=", 1)[0] + "&Subscription-Key=REDACTED"
