# observability-in-practice

Knjiga koja opisuje implementaciju observability sistema (OpenTelemetry +
Grafana LGTM stack) na nivou cele firme, zasnovana na stvarnoj produkcionoj
implementaciji. Sva imena firme, ljudi, interni domeni i ID-jevi resursa su
uklonjeni ili generalizovani.

[![Docs](https://github.com/predrag86/observability-in-practice/actions/workflows/docs.yml/badge.svg)](https://github.com/predrag86/observability-in-practice/actions/workflows/docs.yml)
[![PR checks](https://github.com/predrag86/observability-in-practice/actions/workflows/pr-check.yml/badge.svg)](https://github.com/predrag86/observability-in-practice/actions/workflows/pr-check.yml)

📖 Pročitaj na: **https://predrag86.github.io/observability-in-practice/**

## Struktura repozitorijuma

- `docs/` — sadržaj knjige (Markdown), po poglavlju/dodatku. Slike i
  dijagrami žive u `docs/diagrams/`. Ovo je jedini izvor istine za sadržaj —
  i za sajt i za PDF-ove (vidi ispod).
- `mkdocs.yml` — konfiguracija sajta (MkDocs + Material tema +
  [mkdocs-static-i18n](https://ultrabug.github.io/mkdocs-static-i18n/) za
  srpsku/englesku verziju).
- `.github/workflows/docs.yml` — build i deploy na GitHub Pages pri svakom
  push-u na `main`.
- `scripts/build_pdf.py` — generiše PDF izdanja po delovima knjige direktno
  iz `docs/*.md` (vidi "PDF izdanja" ispod).

## Jezici

Srpska verzija je podrazumevana (`docs/*.md`). Engleski prevod se dodaje
postepeno kao `docs/*.en.md` — dok prevod ne postoji za neku stranicu, sajt
automatski prikazuje srpsku verziju (`fallback_to_default`).

## Lokalni development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-docs.txt
mkdocs serve
```

Sajt je dostupan na `http://127.0.0.1:8000/`.

## PDF izdanja

PDF booklet-i po delovima knjige se generišu direktno iz `docs/*.md` preko
`scripts/build_pdf.py` — nema odvojene, ručno održavane kopije sadržaja za
PDF. Izmena u `docs/` automatski važi i za sledeći PDF build.

Sistemski zahtevi (Debian/Ubuntu):

```bash
apt-get install -y pandoc texlive-xetex texlive-latex-extra fonts-liberation
```

Build:

```bash
python3 scripts/build_pdf.py            # svi delovi
python3 scripts/build_pdf.py deo5 dodaci  # samo izabrani delovi
```

Rezultat ide u `pdf/` (build međurezultati u `pdf-build/`) — oba su
regenerabilni build artefakti i nisu u git-u (vidi `.gitignore`).
