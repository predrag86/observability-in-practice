# observability-in-practice

Knjiga koja opisuje implementaciju observability sistema (OpenTelemetry +
Grafana LGTM stack) na nivou cele firme, zasnovana na stvarnoj produkcionoj
implementaciji. Sva imena firme, ljudi, interni domeni i ID-jevi resursa su
uklonjeni ili generalizovani.

📖 Pročitaj na: **https://predrag86.github.io/observability-in-practice/**

## Struktura repozitorijuma

- `docs/` — sadržaj knjige (Markdown), po poglavlju/dodatku. Slike i
  dijagrami žive u `docs/diagrams/`.
- `mkdocs.yml` — konfiguracija sajta (MkDocs + Material tema +
  [mkdocs-static-i18n](https://ultrabug.github.io/mkdocs-static-i18n/) za
  srpsku/englesku verziju).
- `.github/workflows/docs.yml` — build i deploy na GitHub Pages pri svakom
  push-u na `main`.

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
