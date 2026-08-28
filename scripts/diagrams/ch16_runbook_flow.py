#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch16-runbook-flow" diagram used in
Poglavlje 16 / Chapter 16 (runbook-ovi / runbooks).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch16-runbook-flow.png was hand-built with no source file kept alongside
it, so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch16_runbook_flow.py sr   # -> docs/diagrams/ch16-runbook-flow.png
    python3 scripts/diagrams/ch16_runbook_flow.py en   # -> docs/diagrams/ch16-runbook-flow.en.png
    python3 scripts/diagrams/ch16_runbook_flow.py all  # both

Structure note: the entry runbook orients the reader first (signature +
at-a-glance) before any branching happens. Only then does a single
decision point -- "what is the symptom's fingerprint?" -- split into
three branches, each leading to its own specific runbook. Orientation
before instruction, not the other way around.
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
        "suffix": "",  # docs/diagrams/ch16-runbook-flow.png (default locale, no suffix)
        "nodes": {
            "alert_arrives": "Alarm stigne u kanal",
            "entry_runbook": "Ulazni runbook:\npročitaj potpis + at-a-glance",
            "fingerprint": "Koji je 'otisak'\nsimptoma?",
            "branch1": "Grana 1:\nnedostatak memorije",
            "branch2": "Grana 2:\nmrežni problem pri\npokretanju",
            "branch3": "Grana 3:\ngreška u aplikaciji",
            "runbook1": "Specifičan runbook 1",
            "runbook2": "Specifičan runbook 2",
            "runbook3": "Specifičan runbook 3",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch16-runbook-flow.en.png
        "nodes": {
            "alert_arrives": "Alert arrives in channel",
            "entry_runbook": "Entry runbook:\nread signature + at-a-glance",
            "fingerprint": "What is the symptom's\nfingerprint?",
            "branch1": "Branch 1:\nout of memory",
            "branch2": "Branch 2:\nnetwork issue at\nstartup",
            "branch3": "Branch 3:\napplication error",
            "runbook1": "Specific runbook 1",
            "runbook2": "Specific runbook 2",
            "runbook3": "Specific runbook 3",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]

    g = Digraph("ch16_runbook_flow", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.55", ranksep="0.65", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("alert_arrives", n["alert_arrives"])
    g.node("entry_runbook", n["entry_runbook"])
    g.node("fingerprint", n["fingerprint"], shape="diamond")
    g.node("branch1", n["branch1"])
    g.node("branch2", n["branch2"])
    g.node("branch3", n["branch3"])
    g.node("runbook1", n["runbook1"])
    g.node("runbook2", n["runbook2"])
    g.node("runbook3", n["runbook3"])

    g.edge("alert_arrives", "entry_runbook")
    g.edge("entry_runbook", "fingerprint")

    g.edge("fingerprint", "branch1")
    g.edge("fingerprint", "branch2")
    g.edge("fingerprint", "branch3")

    g.edge("branch1", "runbook1")
    g.edge("branch2", "runbook2")
    g.edge("branch3", "runbook3")

    out_path = OUT_DIR / f"ch16-runbook-flow{cfg['suffix']}.png"
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
