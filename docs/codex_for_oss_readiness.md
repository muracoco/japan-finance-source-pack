# Codex for OSS Readiness

This note summarizes the repository's current fit for a Codex for OSS application.

## 1. Selection Criteria

The repository is structured as a maintainable OSS project:

- Public purpose: repeatable source-pack JSON generation for Japanese equity research.
- Ecosystem relevance: helps separate durable public filings, exchange statistics, optional API data, company IR leads, and current follow-up fields.
- Maintenance surface: source provenance review, schema compatibility, optional connector behavior, issue triage, PR review, CI, and tagged releases.
- Current project hygiene: README, license, security policy, contributing guide, issue templates, pull request template, CI, tests, schema docs, and mock example output.

Current limitation:

- The project is still early. Usage, external contributors, issue history, and release history should be built up through small public issues and a `v0.1.0` release.

## 2. Public Repository Safety

The repository is intended to be safe as a public repository when these boundaries are preserved:

- No real `.env` files, credentials, tokens, cookies, private keys, downloaded filings, generated reports, private research notes, screenshots, spreadsheets, PDFs, or caches.
- `.env.example` may remain because it contains empty placeholder variables only.
- Examples should stay mock or clearly non-sensitive.
- Company IR search candidates must remain non-primary leads until a human verifies the official company domain, document date, and site terms.
- Generated files under `outputs/` should remain ignored.

Recommended public checks:

- Run `python -m pytest`.
- Run an offline smoke command with `--validate`.
- Search the worktree for credential-like terms before releases.
- Confirm GitHub secret scanning has no alerts for the public repository.

## 3. Further Improvements

Near-term improvements that strengthen the OSS application:

- Publish a small `v0.1.0` release with release notes.
- Open public issues for schema validation, sample output quality, optional connector normalization, and JPX/EDINET follow-up work.
- Add a short usage example showing a generated source-pack excerpt.
- Keep issue labels and release notes aligned with bugs, source coverage, connector work, documentation, and schema changes.

Longer-term improvements:

- Add explicit EDINET document retrieval behind a user flag.
- Normalize J-Quants field names while documenting delay and plan limitations.
- Expand JPX CSV support without writing downloaded exchange files.
- Add more tests around connector failure modes and schema stability.
