from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .common import write_json
from .company_ir import company_ir_candidates
from .edinet import edinet_document_metadata
from .edinetdb import edinetdb_company_profile
from .jpx import jpx_public_candidates
from .jquants import jquants_daily_quotes, jquants_financial_statements, jquants_listed_info
from .validation import validate_pack

SCHEMA_VERSION = "0.1"

CHATGPT_REQUIRED_FIELDS = [
    "latest_stock_price",
    "latest_market_cap",
    "latest_price_to_book_ratio",
    "52_week_high_low",
    "200_day_moving_average_position",
    "rsi",
    "bollinger_bands",
    "analyst_target_price",
    "rating_consensus",
    "earnings_consensus",
    "latest_news",
    "price_reaction_after_latest_earnings",
    "latest_peer_valuation",
    "final_investment_view",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build source-pack JSON for Japanese equity research.")
    parser.add_argument("--code", required=True, help="Security code, for example 7203.")
    parser.add_argument("--name", required=True, help="Company name.")
    parser.add_argument("--market", default="TSE", help="Market label.")
    parser.add_argument("--date", required=True, help="Analysis date as YYYYMMDD.")
    parser.add_argument("--skip-jpx", action="store_true", help="Skip JPX public source discovery.")
    parser.add_argument(
        "--parse-jpx-csv",
        action="store_true",
        help="Fetch and sample CSV file candidates from JPX pages without writing downloads.",
    )
    parser.add_argument("--skip-edinet", action="store_true", help="Skip EDINET metadata discovery.")
    parser.add_argument("--skip-edinetdb", action="store_true", help="Skip EDINET DB company profile lookup.")
    parser.add_argument("--skip-jquants", action="store_true", help="Skip J-Quants Free retrieval.")
    parser.add_argument("--output", default="", help="Output JSON path.")
    parser.add_argument("--validate", action="store_true", help="Validate the generated source pack before writing.")
    return parser.parse_args()


def empty_pack(args: argparse.Namespace) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "stock": {
            "code": args.code,
            "name": args.name,
            "market": args.market,
            "analysis_date": args.date,
        },
        "retrieved_sources": {
            "jpx_public": [],
            "edinet": [],
            "edinetdb": [],
            "jquants_free": [],
            "company_ir": [],
        },
        "extracted_facts": {
            "filing_metadata": [],
            "company_profile": [],
            "listed_info": [],
            "daily_quotes": [],
            "financial_statements": [],
            "market_structure": [],
            "ir_documents": [],
        },
        "chatgpt_required_fields": CHATGPT_REQUIRED_FIELDS,
        "limitations": [],
    }


def add_limitations(pack: dict, limitations: list[str]) -> None:
    for limitation in limitations:
        if limitation and limitation not in pack["limitations"]:
            pack["limitations"].append(limitation)


def build_pack(args: argparse.Namespace) -> dict:
    pack = empty_pack(args)

    ir_sources, ir_limitations = company_ir_candidates(args.code, args.name)
    pack["retrieved_sources"]["company_ir"] = ir_sources
    add_limitations(pack, ir_limitations)

    if not args.skip_jpx:
        jpx_sources, jpx_limitations = jpx_public_candidates(parse_csv=args.parse_jpx_csv)
        pack["retrieved_sources"]["jpx_public"] = jpx_sources
        add_limitations(pack, jpx_limitations)

    if not args.skip_edinet:
        edinet_sources, filing_metadata, edinet_limitations = edinet_document_metadata(args.date, args.code)
        pack["retrieved_sources"]["edinet"] = edinet_sources
        pack["extracted_facts"]["filing_metadata"] = filing_metadata
        add_limitations(pack, edinet_limitations)

    if not args.skip_edinetdb:
        edinetdb_sources, company_profile, edinetdb_limitations = edinetdb_company_profile(args.code)
        pack["retrieved_sources"]["edinetdb"] = edinetdb_sources
        pack["extracted_facts"]["company_profile"] = company_profile
        add_limitations(pack, edinetdb_limitations)

    if not args.skip_jquants:
        jquants_sources, listed_info, jquants_limitations = jquants_listed_info(args.code)
        daily_sources, daily_quotes, daily_limitations = jquants_daily_quotes(args.code, args.date)
        statement_sources, statements, statement_limitations = jquants_financial_statements(args.code)
        pack["retrieved_sources"]["jquants_free"] = jquants_sources + daily_sources + statement_sources
        pack["extracted_facts"]["listed_info"] = listed_info
        pack["extracted_facts"]["daily_quotes"] = daily_quotes
        pack["extracted_facts"]["financial_statements"] = statements
        add_limitations(pack, jquants_limitations + daily_limitations + statement_limitations)

    return pack


def main() -> int:
    args = parse_args()
    output = Path(args.output) if args.output else Path("outputs") / f"source_pack_{args.code}_{args.date}.json"
    pack = build_pack(args)
    if args.validate:
        errors = validate_pack(pack)
        if errors:
            for error in errors:
                print(f"validation error: {error}", file=sys.stderr)
            return 1
    write_json(output, pack)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
