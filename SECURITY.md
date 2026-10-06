# Security Policy

## Reporting

Please do not open public issues for credential leaks or sensitive data exposure.

Report security concerns privately to the repository maintainer.

## Sensitive Data Rules

This project must not contain:

- API keys, tokens, passwords, cookies, or private keys
- `.env` files other than `.env.example`
- Downloaded filings, generated reports, private notes, screenshots, or cache files
- Non-public company or personal data

If sensitive data is accidentally committed, rotate the affected credential before removing it from history.

## Public Commit Identity

The maintainer uses GitHub's private commit email:

```sh
git config user.email "207765797+muracoco@users.noreply.github.com"
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
```

Keep GitHub email privacy and push protection enabled. Inspect staged files and
commit metadata before publishing. Email settings affect future commits only;
ignore rules do not remove already tracked data. After a privacy history rewrite,
use a fresh clone instead of merging or force-pushing an older clone. Keep recovery
backups private. Actions records can retain references to previous public commits
and need separate review when removing an exposure.
