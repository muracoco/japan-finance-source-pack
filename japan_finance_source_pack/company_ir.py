from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

from .common import source

HUMAN_VERIFICATION_LIMITATIONS = [
    "Human verification is required before using this candidate as source evidence.",
    "The official company domain, document date, and site terms must be checked manually.",
]

@dataclass(frozen=True)
class IrSearchTarget:
    keyword: str
    document_type: str
    source_type: str


IR_SEARCH_TARGETS = [
    IrSearchTarget("earnings release", "earnings_release", "company_ir_earnings_search_candidate"),
    IrSearchTarget("earnings presentation", "earnings_presentation", "company_ir_presentation_search_candidate"),
    IrSearchTarget("medium term plan", "medium_term_plan", "company_ir_strategy_search_candidate"),
    IrSearchTarget("share buyback", "buyback_release", "company_ir_capital_policy_search_candidate"),
    IrSearchTarget("dividend policy", "dividend_policy", "company_ir_capital_policy_search_candidate"),
    IrSearchTarget("integrated report", "integrated_report", "company_ir_report_search_candidate"),
]

IR_PAGE_QUERIES = [
    ("investor relations", "ir_page"),
    ("IR library", "ir_library"),
    ("financial results", "financial_results_page"),
]


def company_ir_candidates(code: str, name: str) -> tuple[list[dict], list[str]]:
    candidates: list[dict] = []
    for target in IR_SEARCH_TARGETS:
        query = f"{name} {code} {target.keyword} IR PDF"
        candidates.append(
            source(
                source_name=f"Company IR search candidate: {target.keyword}",
                source_type=target.source_type,
                source_url=f"https://www.google.com/search?q={quote_plus(query)}",
                is_primary_source=False,
                data_delay_note="Search candidate only. Verify the official company IR page before using facts.",
                limitations=[
                    "This project does not bulk-download company IR PDFs.",
                    *HUMAN_VERIFICATION_LIMITATIONS,
                ],
                title=f"{name} {target.keyword}",
                inferred_document_type=target.document_type,
                query=query,
            )
        )

    for keyword, page_type in IR_PAGE_QUERIES:
        query = f"{name} {code} {keyword}"
        candidates.append(
            source(
                source_name=f"Company IR page search candidate: {keyword}",
                source_type="company_ir_page_search_candidate",
                source_url=f"https://www.google.com/search?q={quote_plus(query)}",
                is_primary_source=False,
                data_delay_note="Search candidate only. Not a retrieved company document.",
                limitations=HUMAN_VERIFICATION_LIMITATIONS,
                title=f"{name} {keyword}",
                inferred_document_type=page_type,
                query=query,
            )
        )

    limitations = [
        "Company IR discovery is limited to search candidates; official document retrieval is intentionally manual.",
        "Company IR candidates are not primary sources until a human verifies the official domain.",
    ]
    return candidates, limitations
