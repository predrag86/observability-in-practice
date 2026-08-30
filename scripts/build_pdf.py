#!/usr/bin/env python3
"""
Build the per-Deo PDF booklets directly from docs/*.md — the same Markdown
source that feeds the MkDocs site. This replaces an earlier, separate pandoc
pipeline that read from a hand-maintained duplicate copy of the chapters:
that duplication was a real risk (a fix made only in docs/ would silently
never reach the PDFs), so this script is now the single source of truth's
enforcement mechanism, not just a convenience.

Usage:
    python3 scripts/build_pdf.py            # build all parts
    python3 scripts/build_pdf.py deo5 dodaci # build only the named parts

Requires: pandoc, a LaTeX engine (xelatex), and the "Liberation Serif" font
family to be installed. On Debian/Ubuntu:
    apt-get install -y pandoc texlive-xetex texlive-latex-extra fonts-liberation
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
BUILD_DIR = REPO_ROOT / "pdf-build"
OUTPUT_DIR = REPO_ROOT / "pdf"
PREAMBLE = REPO_ROOT / "scripts" / "pdf" / "preamble.tex"

BOOK_TITLE = "OBSERVABILITY U PRAKSI"
BOOK_SUBTITLE = "OpenTelemetry i Grafana LGTM stack"
AUTHOR = "Predrag Mujkovic"
DATE = "Avgust 2026."

# Each part mirrors one PDF booklet from the original hand-run pandoc
# pipeline. "files" lists docs/*.md filenames in reading order.
PARTS = [
    {
        "key": "uvod-3",
        "out": "observability-uvod-do-poglavlja-3.pdf",
        "files": [
            "uvod.md",
            "deo-1-uvod.md",
            "poglavlje-01-sta-je-observability.md",
            "poglavlje-02-opentelemetry.md",
            "poglavlje-03-izbor-platforme.md",
        ],
        "kicker": "Radna verzija --- prva poglavlja",
        "big": "UVOD -- POGLAVLJE 3",
        "sub1": "Temelji observability-ja",
        "sub2": "od pojma do izbora platforme",
        "header_lo": "Uvod -- Poglavlje 3",
    },
    {
        "key": "deo2",
        "out": "observability-deo2-poglavlja-4-9.pdf",
        "files": [
            "deo-2-uvod.md",
            "poglavlje-04-gateway.md",
            "poglavlje-05-instrumentacija.md",
            "poglavlje-06-sidecar.md",
            "poglavlje-07-pull-obrasci.md",
            "poglavlje-08-frontend-rum.md",
            "poglavlje-09-sinteticko-pracenje.md",
        ],
        "kicker": "Radna verzija --- Deo II",
        "big": "DEO II",
        "sub1": "Arhitektura prikupljanja telemetrije",
        "sub2": "uvod + poglavlja 4--9",
        "header_lo": "Deo II",
    },
    {
        "key": "deo3",
        "out": "observability-deo3-poglavlja-10-12.pdf",
        "files": [
            "deo-3-uvod.md",
            "poglavlje-10-anatomija-pipeline.md",
            "poglavlje-11-kardinalnost-cena.md",
            "poglavlje-12-sampling-trejsova.md",
        ],
        "kicker": "Radna verzija --- Deo III",
        "big": "DEO III",
        "sub1": "Pipeline, kardinalnost i sampling",
        "sub2": "poglavlja 10--12",
        "header_lo": "Deo III",
    },
    {
        "key": "deo4",
        "out": "observability-deo4-poglavlja-13-17.pdf",
        "files": [
            "deo-4-uvod.md",
            "poglavlje-13-arhitektura-alarmiranja.md",
            "poglavlje-14-kad-alarm-cuti.md",
            "poglavlje-15-slo-budzet-greske.md",
            "poglavlje-16-runbook-ovi.md",
            "poglavlje-17-postmortem-kultura.md",
        ],
        "kicker": "Radna verzija --- Deo IV",
        "big": "DEO IV",
        "sub1": "Alarmiranje, SLO i odgovor na incidente",
        "sub2": "poglavlja 13--17",
        "header_lo": "Deo IV",
    },
    {
        "key": "deo5",
        "out": "observability-deo5-poglavlja-18-24.pdf",
        "files": [
            "deo-5-uvod.md",
            "poglavlje-18-baze-podataka.md",
            "poglavlje-19-samostalni-klaster.md",
            "poglavlje-20-autentikacija-iam.md",
            "poglavlje-21-hostovi-serveri.md",
            "poglavlje-22-mreza-ravan-posmatranja.md",
            "poglavlje-23-batch-etl-flota.md",
            "poglavlje-24-snowflake-servis-koji-nije-nas.md",
        ],
        "kicker": "Radna verzija --- Deo V",
        "big": "DEO V",
        "sub1": "Domenske studije slučaja",
        "sub2": "poglavlja 18--24",
        "header_lo": "Deo V",
    },
    {
        "key": "deo6",
        "out": "observability-deo6-poglavlja-25-28.pdf",
        "files": [
            "deo-6-uvod.md",
            "poglavlje-25-privatnost-telemetriji.md",
            "poglavlje-26-soc2-kontrola.md",
            "poglavlje-27-prioritizacija.md",
            "poglavlje-28-ai-asistirana-observability.md",
        ],
        "kicker": "Radna verzija --- Deo VI",
        "big": "DEO VI",
        "sub1": "Upravljanje, usklađenost i zrelost",
        "sub2": "poglavlja 25--28",
        "header_lo": "Deo VI",
    },
    {
        "key": "deo7",
        "out": "observability-deo7-poglavlja-29-31.pdf",
        "files": [
            "deo-7-uvod.md",
            "poglavlje-29-fazni-rollout.md",
            "poglavlje-30-merenje-zrelosti.md",
            "poglavlje-31-zakljucak.md",
        ],
        "kicker": "Radna verzija --- Deo VII",
        "big": "DEO VII",
        "sub1": "Sazrevanje programa",
        "sub2": "poglavlja 29--31",
        "header_lo": "Deo VII",
    },
    {
        "key": "dodaci",
        "out": "observability-dodaci-a-d.pdf",
        "files": [
            "dodatak-a-promql-logql-recepti.md",
            "dodatak-b-recnik-pojmova.md",
            "dodatak-c-checklist-onboarding.md",
            "dodatak-d-sabloni.md",
        ],
        "kicker": "Radna verzija --- Dodaci",
        "big": "DODACI",
        "sub1": "Referentni materijal",
        "sub2": "A -- D",
        "header_lo": "Dodaci A--D",
    },
]

# docs/*.md uses the attr_list image syntax MkDocs/Material need:
#   ![alt](path){: width="90%" }
# pandoc's own markdown reader wants:
#   ![alt](path){width=90%}
ATTR_LIST_IMG_RE = re.compile(r'\{:\s*width="(\d+%)"\s*\}')


def convert_attr_list(markdown_text: str) -> str:
    return ATTR_LIST_IMG_RE.sub(r"{width=\1}", markdown_text)


def build_titlepage(part: dict) -> str:
    return (
        "\\begin{titlepage}\n"
        "\\thispagestyle{empty}\n"
        "\\begin{center}\n"
        "\\vspace*{1.4cm}\n"
        "\\includegraphics[width=0.34\\linewidth]{docs/diagrams/cover-emblem.png}\\\\[1.0cm]\n"
        f"{{\\small\\itshape\\color{{accentcolor}} {part['kicker']}}}\\\\[1.6cm]\n"
        f"{{\\Large\\color{{accentcolor}} {BOOK_TITLE}}}\\\\[4pt]\n"
        f"{{\\small {BOOK_SUBTITLE}}}\\\\[2.6cm]\n"
        "{\\color{rulecolor}\\rule{0.35\\linewidth}{0.6pt}}\\\\[1.2cm]\n"
        f"{{\\huge\\itshape\\bfseries {part['big']}}}\\\\[10pt]\n"
        f"{{\\LARGE\\itshape {part['sub1']}}}\\\\[4pt]\n"
        f"{{\\Large\\itshape\\color{{accentcolor}} {part['sub2']}}}\\\\[2.6cm]\n"
        "{\\color{rulecolor}\\rule{0.35\\linewidth}{0.6pt}}\n"
        "\\vfill\n"
        f"{{\\small {AUTHOR}}}\\\\\n"
        f"{{\\small {DATE}}}\n"
        "\\end{center}\n"
        "\\end{titlepage}\n"
    )


def build_header_override(part: dict) -> str:
    # Redefine the running-header short label for this part. Re-declared in
    # the body (not the shared preamble) so every part can set its own text
    # without hand-editing a shared file per run, which is what the original
    # pipeline did.
    return (
        "```{=latex}\n"
        f"\\fancyhead[LO]{{\\small\\itshape {part['header_lo']}}}\n"
        f"\\fancyhead[RE]{{\\small\\itshape Observability u praksi}}\n"
        "```\n"
    )


def assemble_part_markdown(part: dict) -> str:
    chapters = []
    for filename in part["files"]:
        path = DOCS_DIR / filename
        text = path.read_text(encoding="utf-8")
        chapters.append(convert_attr_list(text).strip())

    body = "\n\n\\newpage\n\n".join(chapters)
    return (
        build_titlepage(part)
        + "\n"
        + build_header_override(part)
        + "\n"
        + body
        + "\n"
    )


def run_pandoc(part: dict, md_path: Path, out_path: Path) -> None:
    cmd = [
        "pandoc",
        str(md_path),
        "-o", str(out_path),
        "--pdf-engine=xelatex",
        "-H", str(PREAMBLE),
        "--top-level-division=chapter",
        f"--resource-path={DOCS_DIR}:.",
        "-V", "mainfont=Liberation Serif",
        "-V", "fontsize=10.5pt",
        "-V", "geometry:paperwidth=6in,paperheight=9in,margin=1in",
        "-V", "linestretch=1.12",
    ]
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def main() -> int:
    requested = set(sys.argv[1:])
    parts = [p for p in PARTS if not requested or p["key"] in requested]
    if requested and len(parts) != len(requested):
        known = {p["key"] for p in PARTS}
        print(f"Unknown part key(s): {requested - known}", file=sys.stderr)
        print(f"Known keys: {sorted(known)}", file=sys.stderr)
        return 1

    BUILD_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    for part in parts:
        print(f"--- building {part['key']} -> {part['out']} ---")
        md = assemble_part_markdown(part)
        md_path = BUILD_DIR / f"{part['key']}.md"
        md_path.write_text(md, encoding="utf-8")
        out_path = OUTPUT_DIR / part["out"]
        run_pandoc(part, md_path, out_path)
        size_kb = out_path.stat().st_size // 1024
        print(f"    wrote {out_path.relative_to(REPO_ROOT)} ({size_kb} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
