# Source Pack Schema

The source pack is an intermediate JSON artifact for Japanese equity research.

```json
{
  "stock": {
    "code": "7203",
    "name": "Toyota Motor",
    "market": "TSE",
    "analysis_date": "20260601"
  },
  "retrieved_sources": {
    "jpx_public": [],
    "edinet": [],
    "edinetdb": [],
    "jquants_free": [],
    "company_ir": []
  },
  "extracted_facts": {
    "filing_metadata": [],
    "company_profile": [],
    "listed_info": [],
    "daily_quotes": [],
    "financial_statements": [],
    "market_structure": [],
    "ir_documents": []
  },
  "chatgpt_required_fields": [],
  "limitations": []
}
```

## Source Object

Each source object should include:

- `source_name`
- `source_type`
- `source_url`
- `retrieved_at`
- `is_primary_source`
- `data_delay_note`
- `limitations`

Source-specific fields can be added when useful, such as `file_candidates`, `title`, `query`, or `row_count`.

JPX file candidates may include `parse_status`, `sample_row_count`, and `sample_rows` when `--parse-jpx-csv` is used. This mode samples CSV candidates in memory and does not write downloaded exchange files.

## Required Follow-Up Fields

The tool intentionally leaves unstable or hard-to-verify fields in `chatgpt_required_fields`, such as:

- latest stock price
- latest market cap
- analyst target price
- rating consensus
- latest news
- final investment view

These fields should be verified at report time from current sources.

## Validation

The CLI can validate the generated shape before writing:

```powershell
python -m japan_finance_source_pack.cli --code 7203 --name "Toyota Motor" --market TSE --date 20260601 --skip-jpx --skip-jquants --validate
```

Validation checks the minimum public contract:

- required top-level keys exist
- `stock.code`, `stock.name`, `stock.market`, and `stock.analysis_date` are non-empty strings
- `retrieved_sources` and `extracted_facts` are objects of lists
- source objects include source name, type, URL, retrieval time, primary-source flag, delay note, and limitations

## Optional Connector Policy

Authenticated connectors must be optional. If an API key is missing, the connector should skip retrieval and add a clear limitation rather than failing the whole workflow.

Planned environment variables:

- `EDINET_API_KEY`
- `EDINETDB_API_KEY`
- `JQUANTS_API_KEY`

Implemented optional connectors:

- EDINET document metadata discovery uses the official EDINET API v2 document-list endpoint and stores filing summaries only.
- EDINET DB company profile lookup uses `X-API-Key` authentication and records the returned company profile as non-primary aggregated data.
- J-Quants retrieval covers listed info, daily quotes, and financial statements when a key is available.

The source pack never writes API keys to `source_url`; EDINET URLs redact `Subscription-Key`.
