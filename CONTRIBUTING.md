# Contributing

Contributions are welcome if they keep the project focused on verifiable public-source evidence.

## Rules

- Do not commit credentials, `.env` files, downloaded filings, generated reports, cache files, or private research notes.
- Prefer official source URLs and explicit limitations over inferred facts.
- Keep generated source-pack fields stable and documented.
- Add or update tests for behavior changes.

## Local Check

Run from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install pytest
python -m pytest
python -m japan_finance_source_pack.cli --code 0000 --name "Sample Company" --market TSE --date 20260601 --offline --validate --output outputs/sample.json
```

The offline command does not use the network, including when API keys are present or `--parse-jpx-csv` is added. Tests use fake keys and responses; real API credentials are not needed.

Check `limitations` when reviewing output. Skipped retrieval, failed retrieval, and a successful request returning no rows are different states. Schema validation does not establish that the source coverage is complete.

Catch `RetrievalError` for remote retrieval failures, not `Exception` for the entire connector. Preserve other successful sources and let programming errors surface. Do not include response bodies, request headers, credential-bearing URLs, or chained transport exceptions in failure messages.
