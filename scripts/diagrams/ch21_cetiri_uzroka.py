#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch21-cetiri-uzroka" diagram used in
Poglavlje 21 / Chapter 21 (hostovi-serveri / hosts-and-servers).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch21-cetiri-uzroka.png was hand-built with no source file kept alongside
it, so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch21_cetiri_uzroka.py sr   # -> docs/diagrams/ch21-cetiri-uzroka.png
    python3 scripts/diagrams/ch21_cetiri_uzroka.py en   # -> docs/diagrams/ch21-cetiri-uzroka.en.png
    python3 scripts/diagrams/ch21_cetiri_uzroka.py all  # both

Structure note: an imported shared dashboard shows "no data" (hexagon,
diagnostic-check node) fanning out into four independent, unrelated
causes (plain boxes) that all produce the same symptom. All four then
converge on one tan "instead of fixing all four" summary node, which in
turn fans out into the two concrete practices that replace chasing every
cause: a USE-method metric set and a threshold rule.
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
        "suffix": "",  # docs/diagrams/ch21-cetiri-uzroka.png (default locale, no suffix)
        "nodes": {
            "dashboard": "Uvezen zajednički\ndashboard",
            "symptom": "Panel pokazuje\n'nema podataka'",
            "cause1": "1. Pogrešan izvor\npodataka\n(UID iz tuđeg\nokruženja)",
            "cause2": "2. Nedostajući kolektor\nobara promenljive\nšablona",
            "cause3": "3. Neusaglašena šema\nimenovanja\n(klasična naspram OTel)",
            "cause4": "4. Agregacija briše\noznake\n(ušteda troška\nplatforme)",
            "summary": "Umesto popravke svih\nčetiri:\nmanji, namerno biran\nsopstveni skup metrika",
            "use": "USE metod po resursu:\nUtilizacija · Zasićenje ·\nGreške",
            "threshold": "Prag =\nmax_over_time(7d)\nnikad trenutna vrednost",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch21-cetiri-uzroka.en.png
        "nodes": {
            "dashboard": "Imported shared\ndashboard",
            "symptom": "Panel shows\n'no data'",
            "cause1": "1. Wrong data\nsource\n(UID from someone\nelse's environment)",
            "cause2": "2. Missing collector\nbreaks template\nvariables",
            "cause3": "3. Mismatched naming\nschema\n(classic vs. OTel)",
            "cause4": "4. Aggregation strips\nlabels\n(platform cost\nsavings)",
            "summary": "Instead of fixing all\nfour:\na smaller, deliberately\nchosen metric set",
            "use": "USE method per resource:\nUtilization · Saturation ·\nErrors",
            "threshold": "Threshold =\nmax_over_time(7d)\nnever the current value",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]

    g = Digraph("ch21_cetiri_uzroka", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.55", ranksep="0.65", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("dashboard", n["dashboard"])
    g.node("symptom", n["symptom"], shape="hexagon", fillcolor=NOTE_FILL,
           color=NOTE_LINE)

    g.node("cause1", n["cause1"])
    g.node("cause2", n["cause2"])
    g.node("cause3", n["cause3"])
    g.node("cause4", n["cause4"])

    g.node("summary", n["summary"], fillcolor=NOTE_FILL, color=NOTE_LINE)

    g.node("use", n["use"])
    g.node("threshold", n["threshold"])

    g.edge("dashboard", "symptom")
    g.edge("symptom", "cause1")
    g.edge("symptom", "cause2")
    g.edge("symptom", "cause3")
    g.edge("symptom", "cause4")

    g.edge("cause1", "summary")
    g.edge("cause2", "summary")
    g.edge("cause3", "summary")
    g.edge("cause4", "summary")

    g.edge("summary", "use")
    g.edge("summary", "threshold")

    out_path = OUT_DIR / f"ch21-cetiri-uzroka{cfg['suffix']}.png"
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
