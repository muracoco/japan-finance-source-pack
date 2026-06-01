from __future__ import annotations

import csv
import re
from io import StringIO
from pathlib import Path
from urllib.parse import urljoin

from .common import http_text, source

JPX_PAGES = {
    "margin_balance": {
        "name": "JPX margin trading statistics",
        "url": "https://www.jpx.co.jp/markets/statistics-equities/margin/index.html",
        "note": "Official JPX page for margin trading statistics.",
    },
    "short_selling_value": {
        "name": "JPX short selling value statistics",
        "url": "https://www.jpx.co.jp/markets/statistics-equities/short-selling/index.html",
        "note": "Official JPX page for short selling value statistics.",
    },
    "short_positions": {
        "name": "JPX short position disclosures",
        "url": "https://www.jpx.co.jp/markets/public/short-selling/index.html",
        "note": "Official JPX page for short position disclosures.",
    },
}


def _file_candidates(page_url: str, limit: int = 12) -> tuple[list[dict], list[str]]:
    try:
        html = http_text(page_url, timeout=30)
    except Exception as exc:  # noqa: BLE001
        return [], [f"JPX page fetch failed: {exc}"]

    hrefs = re.findall(r'href=["\']([^"\']+\.(?:csv|xls|xlsx|pdf|zip))["\']', html, flags=re.I)
    seen: set[str] = set()
    candidates: list[dict] = []
    for href in hrefs:
        url = urljoin(page_url, href)
        if url in seen:
            continue
        seen.add(url)
        candidates.append(
            {
                "url": url,
                "filename": Path(url.split("?", 1)[0]).name,
                "status": "official_file_candidate",
            }
        )
        if len(candidates) >= limit:
            break

    limitations = [] if candidates else ["No downloadable CSV/XLS/XLSX/PDF/ZIP links were detected on the JPX page."]
    return candidates, limitations


def jpx_public_candidates(parse_csv: bool = False) -> tuple[list[dict], list[str]]:
    sources: list[dict] = []
    limitations: list[str] = []
    for source_type, item in JPX_PAGES.items():
        file_candidates, source_limitations = _file_candidates(item["url"])
        if parse_csv:
            csv_limitations = _add_csv_samples(file_candidates)
            source_limitations.extend(csv_limitations)
        limitations.extend(source_limitations)
        sources.append(
            source(
                source_name=item["name"],
                source_type=source_type,
                source_url=item["url"],
                is_primary_source=True,
                data_delay_note=item["note"],
                limitations=source_limitations,
                file_candidates=file_candidates,
            )
        )
    return sources, limitations


def _add_csv_samples(file_candidates: list[dict], sample_size: int = 5) -> list[str]:
    limitations: list[str] = []
    for candidate in file_candidates:
        url = str(candidate.get("url") or "")
        if not url.lower().split("?", 1)[0].endswith(".csv"):
            candidate["parse_status"] = "skipped_non_csv"
            continue
        try:
            text = http_text(url, timeout=30)
            rows = list(csv.DictReader(StringIO(text)))
        except Exception as exc:  # noqa: BLE001
            candidate["parse_status"] = "csv_parse_failed"
            limitations.append(f"JPX CSV candidate parse failed: {exc}")
            continue
        candidate["parse_status"] = "csv_sampled"
        candidate["sample_row_count"] = len(rows)
        candidate["sample_rows"] = rows[:sample_size]

    if file_candidates and not any(item.get("parse_status") == "csv_sampled" for item in file_candidates):
        limitations.append("JPX parse mode found no CSV candidates to sample; non-CSV files were left as candidates.")
    return limitations
