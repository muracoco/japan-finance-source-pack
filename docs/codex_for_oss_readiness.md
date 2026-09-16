# Codex for OSS: Current Project Record

This project builds schema-versioned JSON source packs for Japanese equity research. It separates source discovery and retrieved data from facts that still need verification. It does not provide investment advice.

## Implemented Improvements

- `--offline` generates Company IR search URLs without connector traffic, even when credentials or CSV retrieval flags are present. Unfetched data stays empty with explicit limitations; schema version `0.1` is unchanged.
- HTTP failure messages omit query strings, URL credentials, response bodies, and the original exception chain.
- Network and JSON response failures become limitations. Other connectors and successful J-Quants endpoints keep their results; programming errors still surface.
- README and CONTRIBUTING include editable installation, offline usage, and guidance for reading partial results.
- Package discovery includes only the Python package, so existing generated output does not break `pip install -e .`.

## Local Verification

```powershell
python -m pip install -e .
python -m pytest -q
python -m japan_finance_source_pack.cli --code 0000 --name "Sample Company" --date 20260601 --offline --validate --output outputs/sample.json
```

The focused tests use fake credentials and responses to cover offline execution, sanitized errors and tracebacks, malformed JSON, and preservation of other sources after a failed request. They do not call the external APIs. Generated smoke output stays under the ignored `outputs/` directory.

## Not Verified

- Real API authentication, current endpoint compatibility, account-plan restrictions, and live source contents have not been tested in this work.
- Offline output contains search leads, not retrieved evidence. Schema validation does not establish completeness, accuracy, or freshness.
- These local checks do not establish external usage or adoption. Application statements about those topics need separate evidence.

Keep credentials, downloaded filings, personal data, and private research out of the repository. Use only mock data in tests and examples.
