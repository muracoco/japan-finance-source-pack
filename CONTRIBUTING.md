# Contributing

Contributions are welcome if they keep the project focused on verifiable public-source evidence.

## Rules

- Do not commit credentials, `.env` files, downloaded filings, generated reports, cache files, or private research notes.
- Prefer official source URLs and explicit limitations over inferred facts.
- Keep generated source-pack fields stable and documented.
- Add or update tests for behavior changes.

## Local Check

```powershell
python -m pytest
python -m japan_finance_source_pack.cli --code 7203 --name "Toyota Motor" --market TSE --date 20260601 --skip-jpx --skip-jquants --output outputs/sample.json
```
