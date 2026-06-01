from __future__ import annotations

from argparse import Namespace

from japan_finance_source_pack.cli import build_pack
from japan_finance_source_pack.validation import validate_pack


def test_build_pack_without_network_flags() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        skip_jquants=True,
        output="",
        validate=False,
    )

    pack = build_pack(args)

    assert pack["stock"]["code"] == "7203"
    assert pack["retrieved_sources"]["company_ir"]
    assert pack["retrieved_sources"]["jpx_public"] == []
    assert pack["retrieved_sources"]["jquants_free"] == []


def test_valid_pack_passes_validation() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        skip_jquants=True,
        output="",
        validate=True,
    )

    assert validate_pack(build_pack(args)) == []


def test_missing_top_level_key_fails_validation() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        skip_jquants=True,
        output="",
        validate=True,
    )
    pack = build_pack(args)
    del pack["stock"]

    assert "missing top-level key: stock" in validate_pack(pack)


def test_missing_stock_code_fails_validation() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        skip_jquants=True,
        output="",
        validate=True,
    )
    pack = build_pack(args)
    pack["stock"]["code"] = ""

    assert "stock.code must be a non-empty string" in validate_pack(pack)


def test_empty_optional_source_lists_are_valid() -> None:
    pack = {
        "stock": {
            "code": "7203",
            "name": "Toyota Motor",
            "market": "TSE",
            "analysis_date": "20260601",
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
        "chatgpt_required_fields": ["latest_stock_price"],
        "limitations": [],
    }

    assert validate_pack(pack) == []
