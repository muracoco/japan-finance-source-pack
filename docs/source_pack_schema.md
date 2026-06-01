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
    "jquants_free": [],
    "company_ir": []
  },
  "extracted_facts": {
    "listed_info": [],
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

## Required Follow-Up Fields

The tool intentionally leaves unstable or hard-to-verify fields in `chatgpt_required_fields`, such as:

- latest stock price
- latest market cap
- analyst target price
- rating consensus
- latest news
- final investment view

These fields should be verified at report time from current sources.
