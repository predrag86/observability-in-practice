#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch17-tri-tipa" diagram used in
Poglavlje 17 / Chapter 17 (postmortem-kultura / postmortem culture).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch17-tri-tipa.png was hand-built with no source file kept alongside it,
so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch17_tri_tipa.py sr   # -> docs/diagrams/ch17-tri-tipa.png
    python3 scripts/diagrams/ch17_tri_tipa.py en   # -> docs/diagrams/ch17-tri-tipa.en.png
    python3 scripts/diagrams/ch17_tri_tipa.py all  # both

Structure note: three documents, three different directions. An incident
produces a postmortem (backward-looking: what happened, why). From the
postmortem, two things can be distilled -- a runbook (forward-looking, for
next time) and/or a handoff (a one-time request handed to a single owner)
-- both dotted, since neither is guaranteed to come out of every
postmortem the way the postmortem itself is guaranteed to follow the
incident.
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch17-tri-tipa.png (default locale, no suffix)
        "nodes": {
            "incident": "Incident se dogodi",
            "postmortem": "Postmortem\n(unazad usmeren)\n'šta se dogodilo, zašto'",
            "runbook": "Runbook\n(unapred usmeren)\n'sledeći put uradi Y'",
            "handoff": "Handoff\n(jednokratan zahtev)\n'ovo mora vlasnik X'",
        },
        "edges": {
            "to_runbook": "distiluje se u",
            "to_handoff": "otkrije rad koji infra\nne može sama da završi",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch17-tri-tipa.en.png
        "nodes": {
            "incident": "An incident happens",
            "postmortem": "Postmortem\n(backward-looking)\n'what happened, why'",
            "runbook": "Runbook\n(forward-looking)\n'next time do Y'",
            "handoff": "Handoff\n(one-time request)\n'this needs owner X'",
        },
        "edges": {
            "to_runbook": "distills into",
            "to_handoff": "surfaces work infra\ncan't finish on its own",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("ch17_tri_tipa", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.55", ranksep="0.85", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("incident", n["incident"])
    g.node("postmortem", n["postmortem"])
    g.node("runbook", n["runbook"])
    g.node("handoff", n["handoff"])

    g.edge("incident", "postmortem")
    g.edge("postmortem", "runbook", label=e["to_runbook"], style="dotted")
    g.edge("postmortem", "handoff", label=e["to_handoff"], style="dotted")

    out_path = OUT_DIR / f"ch17-tri-tipa{cfg['suffix']}.png"
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
