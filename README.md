# Japan Finance Source Pack

`japan-finance-source-pack` builds a small JSON source pack for Japanese equity research.

The goal is to separate source discovery from final investment analysis. The tool collects or points to public-source evidence that a human analyst or an AI assistant can verify before writing a report.

## What It Does

- Creates a structured source-pack JSON for a Japanese listed company.
- Adds official JPX public data pages and downloadable file candidates.
- Adds company IR search candidates without bulk-downloading PDFs.
- Optionally retrieves J-Quants listed information when `JQUANTS_API_KEY` is set.
- Leaves unstable market fields, analyst estimates, and final judgment as explicit follow-up fields.

## Why This Exists

Japanese equity research often mixes durable public filings, exchange statistics, delayed market data, and current news. This project keeps those layers separate. It produces a small, reviewable JSON artifact that records what was found, where it came from, and what still needs current verification.

That makes the workflow useful for:

- maintaining repeatable research handoffs
- checking whether an analysis has source coverage
- giving AI assistants structured evidence instead of loose notes
- avoiding accidental treatment of stale market data as current facts

## What It Does Not Do

- It does not provide investment advice.
- It does not scrape private or authenticated web pages.
- It does not store API credentials in the repository.
- It does not claim that discovered search results are official sources.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip pytest
```

No runtime third-party dependency is required for the current minimal version.

## Usage

```powershell
python -m japan_finance_source_pack.cli --code 7203 --name "Toyota Motor" --market TSE --date 20260601 --skip-jquants
```

By default, the command writes:

```text
outputs/source_pack_7203_20260601.json
```

For an offline-safe smoke run:

```powershell
python -m japan_finance_source_pack.cli --code 7203 --name "Toyota Motor" --market TSE --date 20260601 --skip-jpx --skip-jquants --output outputs/sample.json
```

## Optional J-Quants

Set `JQUANTS_API_KEY` in your local shell if you want to try J-Quants retrieval.

```powershell
$env:JQUANTS_API_KEY = "..."
```

Do not commit `.env`, tokens, downloaded filings, generated reports, or cache files.

## Roadmap

- Add EDINET filing metadata discovery.
- Add source-pack validation.
- Add richer examples that use mock or public non-sensitive sample data.
- Add adapters for other official Japanese market data pages.
- Keep the schema stable enough for downstream report-generation tools.

## Maintainer Notes

This repository is intentionally conservative. New data connectors should prefer official public pages, document known delays, and fail with explicit limitations rather than silently guessing.

## Output Shape

See [docs/source_pack_schema.md](docs/source_pack_schema.md).

## Project Status

This is an early OSS extraction from a local research workflow. The public version intentionally starts small: source discovery, stable JSON shape, and clear limitations before broader data retrieval is added.

## License

MIT. See [LICENSE](LICENSE).
