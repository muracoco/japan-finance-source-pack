from __future__ import annotations

from argparse import Namespace

from japan_finance_source_pack.cli import build_pack
from japan_finance_source_pack import edinet
from japan_finance_source_pack import edinetdb
from japan_finance_source_pack import jpx
from japan_finance_source_pack import jquants
from japan_finance_source_pack.validation import validate_pack


def test_build_pack_without_network_flags() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=False,
    )

    pack = build_pack(args)

    assert pack["schema_version"] == "0.1"
    assert pack["stock"]["code"] == "7203"
    assert pack["retrieved_sources"]["company_ir"]
    assert pack["retrieved_sources"]["jpx_public"] == []
    assert pack["retrieved_sources"]["edinet"] == []
    assert pack["retrieved_sources"]["edinetdb"] == []
    assert pack["retrieved_sources"]["jquants_free"] == []


def test_company_ir_candidates_use_specific_source_types() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=False,
    )

    source_types = {item["source_type"] for item in build_pack(args)["retrieved_sources"]["company_ir"]}

    assert "company_ir_earnings_search_candidate" in source_types
    assert "company_ir_presentation_search_candidate" in source_types
    assert "company_ir_report_search_candidate" in source_types


def test_company_ir_candidates_include_multiple_ir_page_queries() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=False,
    )

    page_types = {
        item["inferred_document_type"]
        for item in build_pack(args)["retrieved_sources"]["company_ir"]
        if item["source_type"] == "company_ir_page_search_candidate"
    }

    assert page_types == {"ir_page", "ir_library", "financial_results_page"}


def test_company_ir_candidates_require_human_verification() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=False,
    )

    pack = build_pack(args)

    assert "Company IR candidates are not primary sources until a human verifies the official domain." in pack["limitations"]
    assert all(
        "Human verification is required before using this candidate as source evidence." in item["limitations"]
        for item in pack["retrieved_sources"]["company_ir"]
    )


def test_company_ir_candidates_stay_non_primary_search_candidates() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=False,
    )

    candidates = build_pack(args)["retrieved_sources"]["company_ir"]

    assert all(item["is_primary_source"] is False for item in candidates)
    assert all(item["source_url"].startswith("https://www.google.com/search?q=") for item in candidates)
    assert all("query" in item for item in candidates)


def test_valid_pack_passes_validation() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
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
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=True,
    )
    pack = build_pack(args)
    del pack["stock"]

    assert "missing top-level key: stock" in validate_pack(pack)


def test_missing_schema_version_fails_validation() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=True,
    )
    pack = build_pack(args)
    del pack["schema_version"]

    errors = validate_pack(pack)

    assert "missing top-level key: schema_version" in errors
    assert "schema_version must be a non-empty string" in errors


def test_missing_stock_code_fails_validation() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=True,
    )
    pack = build_pack(args)
    pack["stock"]["code"] = ""

    assert "stock.code must be a non-empty string" in validate_pack(pack)


def test_invalid_source_url_fails_validation() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=True,
    )
    pack = build_pack(args)
    pack["retrieved_sources"]["company_ir"][0]["source_url"] = "not-a-url"

    assert "retrieved_sources.company_ir[0].source_url must be an http(s) URL" in validate_pack(pack)


def test_company_ir_candidate_validation_requires_search_metadata() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=True,
        skip_edinetdb=True,
        skip_jquants=True,
        output="",
        validate=True,
    )
    pack = build_pack(args)
    candidate = pack["retrieved_sources"]["company_ir"][0]
    candidate["is_primary_source"] = True
    candidate["query"] = ""
    del candidate["inferred_document_type"]

    errors = validate_pack(pack)

    assert (
        "retrieved_sources.company_ir[0].is_primary_source must be false for company IR search candidates"
        in errors
    )
    assert "retrieved_sources.company_ir[0].query must be a non-empty string for company IR search candidates" in errors
    assert (
        "retrieved_sources.company_ir[0].inferred_document_type must be a non-empty string for company IR search candidates"
        in errors
    )


def test_jpx_source_validation_requires_primary_source_and_candidate_list() -> None:
    pack = {
        "schema_version": "0.1",
        "stock": {
            "code": "7203",
            "name": "Toyota Motor",
            "market": "TSE",
            "analysis_date": "20260601",
        },
        "retrieved_sources": {
            "jpx_public": [
                {
                    "source_name": "JPX margin trading statistics",
                    "source_type": "margin_balance",
                    "source_url": "https://www.jpx.co.jp/markets/statistics-equities/margin/index.html",
                    "retrieved_at": "2026-06-01T00:00:00+09:00",
                    "is_primary_source": False,
                    "data_delay_note": "Official JPX page for margin trading statistics.",
                    "limitations": [],
                    "file_candidates": "not-a-list",
                }
            ],
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
        "chatgpt_required_fields": ["latest_stock_price"],
        "limitations": [],
    }

    errors = validate_pack(pack)

    assert "retrieved_sources.jpx_public[0].is_primary_source must be true for JPX public sources" in errors
    assert "retrieved_sources.jpx_public[0].file_candidates must be a list when present" in errors


def test_empty_optional_source_lists_are_valid() -> None:
    pack = {
        "schema_version": "0.1",
        "stock": {
            "code": "7203",
            "name": "Toyota Motor",
            "market": "TSE",
            "analysis_date": "20260601",
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
        "chatgpt_required_fields": ["latest_stock_price"],
        "limitations": [],
    }

    assert validate_pack(pack) == []


def test_missing_optional_api_keys_leave_limitations() -> None:
    args = Namespace(
        code="7203",
        name="Toyota Motor",
        market="TSE",
        date="20260601",
        skip_jpx=True,
        parse_jpx_csv=False,
        skip_edinet=False,
        skip_edinetdb=False,
        skip_jquants=False,
        output="",
        validate=True,
    )

    pack = build_pack(args)

    assert validate_pack(pack) == []
    assert "EDINET_API_KEY is not set; EDINET metadata discovery was skipped." in pack["limitations"]
    assert "EDINETDB_API_KEY is not set; EDINET DB lookup was skipped." in pack["limitations"]
    assert "JQUANTS_API_KEY is not set; listed-info retrieval was skipped." in pack["limitations"]
    assert "JQUANTS_API_KEY is not set; daily-quotes retrieval was skipped." in pack["limitations"]
    assert "JQUANTS_API_KEY is not set; financial-statements retrieval was skipped." in pack["limitations"]


def test_edinet_document_summary_adds_document_category() -> None:
    summary = edinet._document_summary(
        {
            "docID": "S100TEST",
            "secCode": "72030",
            "docTypeCode": "120",
            "filerName": "Sample Company",
        }
    )

    assert summary["document_category"] == "annual_securities_report"
    assert summary["docID"] == "S100TEST"


def test_jquants_format_date_accepts_yyyymmdd_and_iso() -> None:
    assert jquants._format_date("20260601") == "2026-06-01"
    assert jquants._format_date("2026-06-01") == "2026-06-01"


def test_edinetdb_company_profile_rows_accepts_data_object_only() -> None:
    assert edinetdb._company_profile_rows({"data": {"code": "7203"}}) == [{"code": "7203"}]
    assert edinetdb._company_profile_rows({"code": "7203"}) == [{"code": "7203"}]
    assert edinetdb._company_profile_rows({"data": []}) == []


def test_jpx_csv_parse_mode_samples_csv_candidates(monkeypatch) -> None:
    def fake_http_text(url: str, timeout: int = 30) -> str:
        return "code,name\n7203,Toyota Motor\n6758,Sony Group\n"

    monkeypatch.setattr(jpx, "http_text", fake_http_text)
    candidates = [{"url": "https://example.test/sample.csv"}]

    limitations = jpx._add_csv_samples(candidates, sample_size=1)

    assert limitations == []
    assert candidates[0]["parse_status"] == "csv_sampled"
    assert candidates[0]["sample_row_count"] == 2
    assert candidates[0]["sample_rows"] == [{"code": "7203", "name": "Toyota Motor"}]


def test_jpx_csv_parse_mode_skips_non_csv_candidates() -> None:
    candidates = [{"url": "https://example.test/sample.xlsx"}]

    limitations = jpx._add_csv_samples(candidates)

    assert candidates[0]["parse_status"] == "skipped_non_csv"
    assert limitations == ["JPX parse mode found no CSV candidates to sample; non-CSV files were left as candidates."]


def test_jpx_csv_parse_mode_accepts_empty_csv_rows(monkeypatch) -> None:
    def fake_http_text(url: str, timeout: int = 30) -> str:
        return "code,name\n"

    monkeypatch.setattr(jpx, "http_text", fake_http_text)
    candidates = [{"url": "https://example.test/empty.csv"}]

    limitations = jpx._add_csv_samples(candidates)

    assert limitations == []
    assert candidates[0]["parse_status"] == "csv_sampled"
    assert candidates[0]["sample_row_count"] == 0
    assert candidates[0]["sample_rows"] == []


def test_jpx_csv_parse_mode_records_parse_failures(monkeypatch) -> None:
    def fake_http_text(url: str, timeout: int = 30) -> str:
        raise TimeoutError("request timed out")

    monkeypatch.setattr(jpx, "http_text", fake_http_text)
    candidates = [{"url": "https://example.test/broken.csv"}]

    limitations = jpx._add_csv_samples(candidates)

    assert candidates[0]["parse_status"] == "csv_parse_failed"
    assert limitations == [
        "JPX CSV candidate parse failed: request timed out",
        "JPX parse mode found no CSV candidates to sample; non-CSV files were left as candidates.",
    ]
