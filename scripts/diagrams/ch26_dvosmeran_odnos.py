#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch26-dvosmeran-odnos" diagram used in
Poglavlje 26 / Chapter 26 (soc2-kontrola / soc2-control).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch26-dvosmeran-odnos.png was hand-built with no source file kept alongside
it, so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch26_dvosmeran_odnos.py sr   # -> docs/diagrams/ch26-dvosmeran-odnos.png
    python3 scripts/diagrams/ch26_dvosmeran_odnos.py en   # -> docs/diagrams/ch26-dvosmeran-odnos.en.png
    python3 scripts/diagrams/ch26_dvosmeran_odnos.py all  # both

Structure note: the "two-way relationship" of the title is the fork out
of the alerting/observability system: it is simultaneously evidence of
control (fed into the compliance status table, marked per glossary
convention as IN PLACE / PARTIAL / GAP) and a carrier of personal data
that itself needs protection (also fed into that same table, since a gap
there is also a documented finding). Both paths converge on the same
status table, which in turn feeds what the auditor actually tests:
consistency between public claims and actual practice.
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"
NOTE_FILL = "#F4EFE6"
NOTE_LINE = "#8B7355"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch26-dvosmeran-odnos.png (default locale, no suffix)
        "nodes": {
            "source": "Sistem alarmiranja\ni posmatranja",
            "evidence": "Nadzor komponenti +\nodgovor na anomalije\n(dokumentovan\nkriterijum)",
            "pii": "Sama telemetrija\npostaje\npoverljiv podatak koji\ntreba zaštititi",
            "table": "Interna tabela stanja\n✅ / ⚠️ / ❌\npo oblasti kontrole",
            "final": "Ono što revizor stvarno\ntestira:\ndoslednost javne tvrdnje\nnaspram stvarne prakse",
        },
        "edges": {
            "evidence": "je DOKAZ kontrole",
            "pii": "nosi lične podatke",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch26-dvosmeran-odnos.en.png
        "nodes": {
            "source": "Alerting and\nobservability system",
            "evidence": "Component monitoring +\nanomaly response\n(documented\ncriterion)",
            "pii": "The telemetry itself\nbecomes\nconfidential data that\nneeds protection",
            "table": "Internal status table\n✅ / ⚠️ / ❌\nby control area",
            "final": "What the auditor\nactually tests:\nconsistency between the\npublic claim and actual\npractice",
        },
        "edges": {
            "evidence": "IS evidence of control",
            "pii": "carries personal data",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("ch26_dvosmeran_odnos", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.5", ranksep="0.85", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("source", n["source"])
    g.node("evidence", n["evidence"])
    g.node("pii", n["pii"])
    g.node("table", n["table"], shape="hexagon", fillcolor=NOTE_FILL, color=NOTE_LINE)
    g.node("final", n["final"], fillcolor=NOTE_FILL, color=NOTE_LINE)

    with g.subgraph() as s:
        s.attr(rank="same")
        s.node("evidence")
        s.node("pii")

    g.edge("source", "evidence", label=e["evidence"])
    g.edge("source", "pii", label=e["pii"])
    g.edge("evidence", "table")
    g.edge("pii", "table")
    g.edge("table", "final")

    out_path = OUT_DIR / f"ch26-dvosmeran-odnos{cfg['suffix']}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g.render(outfile=str(out_path), cleanup=True)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    targets = sys.argv[1:] or ["en"]
    if targets == ["all"]:
        targets = list(LANGUAGES.keys())
    for t in targets:
        if t not in LANGUAGES:
            raise SystemExit(f"unknown language {t!r}, known: {list(LANGUAGES)}")
        render(t)
