# Publish Checklist

Repository name:

```text
muracoco/japan-finance-source-pack
```

Suggested description:

```text
Build source-pack JSON for Japanese equity research from public sources.
```

Suggested topics:

```text
japan finance equity-research jpx jquants source-pack python oss
```

GitHub About fields:

```text
Description: Build source-pack JSON for Japanese equity research from public sources.
Website: leave blank
Topics: japan, finance, equity-research, jpx, jquants, source-pack, python, oss
```

Before making the repository public:

- [ ] Confirm no `.env` files exist except `.env.example`.
- [ ] Confirm no downloaded filings, generated reports, images, spreadsheets, PDFs, or cache files are present.
- [ ] Confirm `README.md`, `LICENSE`, `SECURITY.md`, and `OPEN_SOURCE_NOTES.md` are present.
- [ ] Install real Python locally and run `python -m pytest`.
- [ ] Run the offline smoke command from `README.md` with `--validate`.
- [ ] Confirm `examples/source_pack_sample.json` contains only mock data.
- [ ] Create three public issues for validation, sample output, and optional API connectors.
- [ ] Keep the first release small and label it `v0.1.0`.
- [ ] Confirm `docs/codex_for_oss_readiness.md` reflects the current public safety boundary and maintenance plan.
- [ ] Confirm GitHub secret scanning has no open alerts.

Suggested initial public issues:

```text
Improve schema validation for source-specific fields
Add generated output excerpt to README
Normalize optional connector response fields
Expand JPX CSV sampling coverage
Prepare v0.1.0 release notes
```

Release checklist:

- [ ] CI passes on Python 3.10, 3.11, and 3.12.
- [ ] Release notes mention schema changes, connector changes, and known limitations.
- [ ] No ignored output, cache, or credential files are staged.

v0.1.1 release checklist:

- [ ] Confirm generated packs include `schema_version: "0.1"`.
- [ ] Confirm `examples/source_pack_sample.json` matches the documented schema.
- [ ] Confirm connector changes remain optional and leave limitations when credentials are missing.
- [ ] Run `python -m pytest -q`.
- [ ] Run the offline smoke command with `--skip-jpx --skip-jquants --skip-edinet --skip-edinetdb --validate`.
- [ ] Confirm no `.env`, cache, downloaded filings, spreadsheets, PDFs, images, or generated outputs are staged.
- [ ] Keep release notes focused on schema metadata, sample/docs sync, and connector safety boundaries.

Initial commit message:

```text
Initial public source-pack extraction
```
