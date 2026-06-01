from __future__ import annotations

import argparse
from pathlib import Path

from .common import write_json
from .company_ir import company_ir_candidates
from .jpx import jpx_public_candidates
from .jquants import jquants_listed_info

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
    parser.add_argument("--skip-jquants", action="store_true", help="Skip J-Quants Free retrieval.")
    parser.add_argument("--output", default="", help="Output JSON path.")
    return parser.parse_args()


def empty_pack(args: argparse.Namespace) -> dict:
    return {
        "stock": {
            "code": args.code,
            "name": args.name,
            "market": args.market,
            "analysis_date": args.date,
        },
        "retrieved_sources": {
            "jpx_public": [],
            "jquants_free": [],
            "company_ir": [],
        },
        "extracted_facts": {
            "listed_info": [],
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
        jpx_sources, jpx_limitations = jpx_public_candidates()
        pack["retrieved_sources"]["jpx_public"] = jpx_sources
        add_limitations(pack, jpx_limitations)

    if not args.skip_jquants:
        jquants_sources, listed_info, jquants_limitations = jquants_listed_info(args.code)
        pack["retrieved_sources"]["jquants_free"] = jquants_sources
        pack["extracted_facts"]["listed_info"] = listed_info
        add_limitations(pack, jquants_limitations)

    return pack


def main() -> int:
    args = parse_args()
    output = Path(args.output) if args.output else Path("outputs") / f"source_pack_{args.code}_{args.date}.json"
    pack = build_pack(args)
    write_json(output, pack)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
