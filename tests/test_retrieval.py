from __future__ import annotations

import csv
import json
import sys
import traceback
from argparse import Namespace
from http.client import IncompleteRead
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

import pytest

from japan_finance_source_pack import cli, common, jpx
from japan_finance_source_pack.validation import validate_pack


@pytest.fixture(autouse=True)
def fake_credentials_and_no_network(monkeypatch):
    for name in ("EDINET_API_KEY", "EDINETDB_API_KEY", "JQUANTS_API_KEY", "JQUANTS_ID_TOKEN"):
        monkeypatch.setenv(name, "fake-test-credential")

    def unexpected_network(*args, **kwargs):
        pytest.fail("Unexpected network access")

    monkeypatch.setattr(common, "urlopen", unexpected_network)


@pytest.fixture
def args():
    return Namespace(
        code="0000", name="Sample Company", market="TSE", date="20260601",
        offline=False, skip_jpx=False, parse_jpx_csv=False,
        skip_edinet=False, skip_edinetdb=False, skip_jquants=False,
    )


def test_offline_cli_ignores_credentials_and_csv_flag(monkeypatch, tmp_path):
    output = tmp_path / "offline.json"
    monkeypatch.setattr(sys, "argv", [
        "source-pack", "--code", "0000", "--name", "Sample Company", "--date", "20260601",
        "--offline", "--parse-jpx-csv", "--validate", "--output", str(output),
    ])

    def unexpected_connector(*args, **kwargs):
        pytest.fail("Offline mode invoked a network connector")

    for name in (
        "jpx_public_candidates", "edinet_document_metadata", "edinetdb_company_profile",
        "jquants_listed_info", "jquants_daily_quotes", "jquants_financial_statements",
    ):
        monkeypatch.setattr(cli, name, unexpected_connector)

    assert cli.main() == 0
    pack = json.loads(output.read_text(encoding="utf-8"))
    assert validate_pack(pack) == []
    assert pack["schema_version"] == "0.1"
    assert pack["retrieved_sources"]["company_ir"]
    assert all(not rows for key, rows in pack["retrieved_sources"].items() if key != "company_ir")
    assert all(not rows for rows in pack["extracted_facts"].values())
    assert all(item["is_primary_source"] is False for item in pack["retrieved_sources"]["company_ir"])
    assert len([note for note in pack["limitations"] if note.startswith("Offline mode:")]) == 4
    assert "fake-test-credential" not in json.dumps(pack)


@pytest.mark.parametrize("fetch", [common.http_json, common.http_text])
@pytest.mark.parametrize("failure", ["http", "network", "timeout", "connection", "incomplete"])
def test_http_errors_do_not_expose_credentials_or_response_bodies(monkeypatch, fetch, failure):
    url = "https://fake-user:fake-password@example.test/data?%53ubscription-Key=fake-query-key&date=20260601#fake-fragment"
    private_message = f"fake-response-body {url} fake-header-key"

    def fake_urlopen(request, timeout):
        if failure == "http":
            raise HTTPError(url, 403, private_message, {}, BytesIO(private_message.encode()))
        if failure == "network":
            raise URLError(private_message)
        if failure == "timeout":
            raise TimeoutError(private_message)
        if failure == "connection":
            raise ConnectionResetError(private_message)
        raise IncompleteRead(private_message.encode())

    monkeypatch.setattr(common, "urlopen", fake_urlopen)
    headers = {"X-API-Key": "fake-header-key"}
    with pytest.raises(common.RetrievalError) as caught:
        fetch(url, headers=headers)

    rendered = str(caught.value) + repr(caught.value) + "".join(traceback.format_exception(caught.value))
    assert "https://example.test/data" in rendered
    assert "fake-" not in rendered
    assert "Subscription-Key" not in rendered
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None
    if failure == "http":
        assert "HTTP 403" in rendered


@pytest.mark.parametrize("body", [b"fake-invalid-json", b"\xfffake-response", b"[]", b"null", b'"fake-value"'])
def test_invalid_json_is_a_sanitized_retrieval_failure(monkeypatch, body):
    monkeypatch.setattr(common, "urlopen", lambda request, timeout: BytesIO(body))
    url = "https://example.test/data?Subscription-Key=fake-query-key"

    with pytest.raises(common.RetrievalError) as caught:
        common.http_json(url)

    assert "JSON" in str(caught.value)
    assert "fake-" not in "".join(traceback.format_exception(caught.value))
    assert caught.value.__context__ is None


@pytest.mark.parametrize(("failed_path", "failed_fact", "failure_note"), [
    ("/api/v2/documents.json", "filing_metadata", "EDINET metadata retrieval failed: HTTP 403"),
    ("/v1/companies/0000", "company_profile", "EDINET DB company profile retrieval failed: Network"),
    ("/v2/listed/info", "listed_info", "J-Quants listed-info retrieval failed: Network"),
    ("/v2/prices/daily_quotes", "daily_quotes", "J-Quants daily-quotes retrieval failed: Invalid JSON"),
    ("/v2/fins/statements", "financial_statements", "J-Quants financial-statements retrieval failed: Expected a JSON object"),
    ("/markets/statistics-equities/margin/index.html", None, "JPX page fetch failed: Network"),
])
def test_connector_failure_preserves_other_sources(monkeypatch, args, failed_path, failed_fact, failure_note):
    responses = {
        "/api/v2/documents.json": {"results": [{"secCode": "00000", "docTypeCode": "120", "docID": "S100TEST"}]},
        "/v1/companies/0000": {"data": {"code": "0000"}},
        "/v2/listed/info": {"info": [{"code": "0000"}]},
        "/v2/prices/daily_quotes": {"daily_quotes": [{"code": "0000"}]},
        "/v2/fins/statements": {"statements": [{"code": "0000"}]},
    }

    def fake_urlopen(request, timeout):
        path = urlsplit(request.full_url).path
        if path == failed_path:
            if failed_fact == "filing_metadata":
                raise HTTPError(request.full_url, 403, "fake-test-credential", {}, BytesIO(b"fake-response-body"))
            if failed_fact == "company_profile":
                raise URLError("fake-test-credential")
            if failed_fact == "listed_info":
                raise TimeoutError("fake-test-credential")
            if failed_fact == "daily_quotes":
                return BytesIO(b"fake-invalid-json")
            if failed_fact == "financial_statements":
                return BytesIO(b"[]")
            raise IncompleteRead(b"fake-response-body")
        if path in responses:
            return BytesIO(json.dumps(responses[path]).encode())
        assert path in {urlsplit(item["url"]).path for item in jpx.JPX_PAGES.values()}
        return BytesIO(b'<a href="/sample.csv">CSV</a>')

    monkeypatch.setattr(common, "urlopen", fake_urlopen)
    pack = cli.build_pack(args)

    assert validate_pack(pack) == []
    for fact in ("filing_metadata", "company_profile", "listed_info", "daily_quotes", "financial_statements"):
        assert len(pack["extracted_facts"][fact]) == (0 if fact == failed_fact else 1)
    assert len(pack["retrieved_sources"]["jquants_free"]) == (2 if failed_fact in {"listed_info", "daily_quotes", "financial_statements"} else 3)
    assert pack["retrieved_sources"]["company_ir"]
    assert any(note.startswith(failure_note) for note in pack["limitations"])
    assert "fake-" not in json.dumps(pack)
    for item in pack["retrieved_sources"]["jpx_public"]:
        if urlsplit(item["source_url"]).path == failed_path:
            assert item["file_candidates"] == []
            assert any(note.startswith(failure_note) for note in item["limitations"])
        else:
            assert item["file_candidates"]


@pytest.mark.parametrize("skip_jpx", [False, True])
def test_pack_does_not_swallow_programming_errors(monkeypatch, args, skip_jpx):
    def broken_urlopen(request, timeout):
        raise TypeError("programming error")

    monkeypatch.setattr(common, "urlopen", broken_urlopen)
    args.skip_jpx = skip_jpx
    with pytest.raises(TypeError, match="programming error"):
        cli.build_pack(args)


@pytest.mark.parametrize("failure", ["timeout", "csv"])
def test_jpx_csv_failure_keeps_other_samples(monkeypatch, failure):
    def fake_urlopen(request, timeout):
        if request.full_url.endswith("broken.csv"):
            if failure == "timeout":
                raise TimeoutError("fake-test-credential")
            return BytesIO(b"name\nfake-response-body" + b"x" * csv.field_size_limit())
        return BytesIO(b"code,name\n0000,Sample Company\n")

    monkeypatch.setattr(common, "urlopen", fake_urlopen)
    candidates = [{"url": "https://example.test/broken.csv"}, {"url": "https://example.test/ok.csv"}]
    limitations = jpx._add_csv_samples(candidates)
    assert candidates[0]["parse_status"] == "csv_parse_failed"
    assert candidates[1]["sample_rows"] == [{"code": "0000", "name": "Sample Company"}]
    assert len(limitations) == 1
    assert "fake-" not in limitations[0]


def test_jpx_csv_does_not_swallow_programming_errors(monkeypatch):
    def broken_http_text(url, timeout):
        raise TypeError("programming error")

    monkeypatch.setattr(jpx, "http_text", broken_http_text)
    with pytest.raises(TypeError, match="programming error"):
        jpx._add_csv_samples([{"url": "https://example.test/sample.csv"}])
