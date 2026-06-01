from __future__ import annotations

from urllib.parse import quote_plus

from .common import source

IR_DOCUMENT_TYPES = [
    ("earnings release", "earnings_release"),
    ("earnings presentation", "earnings_presentation"),
    ("medium term plan", "medium_term_plan"),
    ("share buyback", "buyback_release"),
    ("dividend policy", "dividend_policy"),
    ("integrated report", "integrated_report"),
]


def company_ir_candidates(code: str, name: str) -> tuple[list[dict], list[str]]:
    candidates: list[dict] = []
    for keyword, document_type in IR_DOCUMENT_TYPES:
        query = f"{name} {code} {keyword} IR PDF"
        candidates.append(
            source(
                source_name=f"Company IR search candidate: {keyword}",
                source_type="company_ir_search_candidate",
                source_url=f"https://www.google.com/search?q={quote_plus(query)}",
                is_primary_source=False,
                data_delay_note="Search candidate only. Verify the official company IR page before using facts.",
                limitations=[
                    "This project does not bulk-download company IR PDFs.",
                    "Users must verify the official domain, document date, and site terms.",
                ],
                title=f"{name} {keyword}",
                inferred_document_type=document_type,
                query=query,
            )
        )

    query = f"{name} {code} investor relations"
    candidates.append(
        source(
            source_name="Company IR page search candidate",
            source_type="company_ir_page_search_candidate",
            source_url=f"https://www.google.com/search?q={quote_plus(query)}",
            is_primary_source=False,
            data_delay_note="Search candidate only. Not a retrieved company document.",
            limitations=["Verify the official company domain before adopting facts."],
            title=f"{name} investor relations",
            inferred_document_type="ir_page",
            query=query,
        )
    )

    limitations = [
        "Company IR discovery is limited to search candidates; official document retrieval is intentionally manual."
    ]
    return candidates, limitations
