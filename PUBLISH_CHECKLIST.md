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

Initial commit message:

```text
Initial public source-pack extraction
```
