# observability-in-practice

A book describing the implementation of an observability system (OpenTelemetry +
Grafana LGTM stack) at the scale of an entire company, based on a real production
implementation. All company names, people, internal domains, and resource IDs
have been removed or generalized.

[![Docs](https://github.com/predrag86/observability-in-practice/actions/workflows/docs.yml/badge.svg)](https://github.com/predrag86/observability-in-practice/actions/workflows/docs.yml)
[![PR checks](https://github.com/predrag86/observability-in-practice/actions/workflows/pr-check.yml/badge.svg)](https://github.com/predrag86/observability-in-practice/actions/workflows/pr-check.yml)

📖 Read it at: **https://predrag86.github.io/observability-in-practice/**
🇬🇧 English edition: **https://predrag86.github.io/observability-in-practice/en/**

## Repository structure

- `docs/` — the book's content (Markdown), by chapter/appendix. Images and
  diagrams live in `docs/diagrams/`. This is the single source of truth for
  content — for both the site and the PDFs (see below).
- `mkdocs.yml` — site configuration (MkDocs + Material theme +
  [mkdocs-static-i18n](https://ultrabug.github.io/mkdocs-static-i18n/) for the
  Serbian/English versions).
- `.github/workflows/docs.yml` — builds and deploys to GitHub Pages on every
  push to `main`.
- `scripts/build_pdf.py` — generates PDF editions by book part directly from
  `docs/*.md` (see "PDF editions" below).

## Languages

The Serbian version is the default (`docs/*.md`). The full English
translation is available as `docs/*.en.md` — the site automatically falls
back to the Serbian version for any page without a translation
(`fallback_to_default`).

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-docs.txt
mkdocs serve
```

The site is available at `http://127.0.0.1:8000/`.

## PDF editions

PDF booklets by book part are generated directly from `docs/*.md` via
`scripts/build_pdf.py` — there's no separate, manually maintained copy of the
content for the PDFs. A change in `docs/` automatically applies to the next
PDF build.

System requirements (Debian/Ubuntu):

```bash
apt-get install -y pandoc texlive-xetex texlive-latex-extra fonts-liberation
```

Build:

```bash
python3 scripts/build_pdf.py              # all parts
python3 scripts/build_pdf.py deo5 dodaci   # only selected parts
```

Output goes to `pdf/` (build intermediates in `pdf-build/`) — both are
regenerable build artifacts and are not in git (see `.gitignore`).
