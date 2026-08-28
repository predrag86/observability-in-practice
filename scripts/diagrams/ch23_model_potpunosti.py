#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch23-model-potpunosti" diagram used in
Poglavlje 23 / Chapter 23 (batch-etl-flota / batch-etl-fleet).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch23-model-potpunosti.png was hand-built with no source file kept
alongside it, so its Serbian labels were baked into raster pixels with no
way to re-render them in English. This script reconstructs the diagram
from one parameterized Graphviz source, so both language variants come
from the same structure.

Usage
-----
    python3 scripts/diagrams/ch23_model_potpunosti.py sr   # -> docs/diagrams/ch23-model-potpunosti.png
    python3 scripts/diagrams/ch23_model_potpunosti.py en   # -> docs/diagrams/ch23-model-potpunosti.en.png
    python3 scripts/diagrams/ch23_model_potpunosti.py all  # both

Structure note: a completeness model for a scheduled/batch job, as a
decision tree. Two decision diamonds ("did it start?", "did it produce
output?") gate three outcomes: never started, ran but failed (with a
further split on whether the cause is transient or permanent), and ran
successfully -- which itself splits into the easily-missed "completed
but zero rows" case (a merged condition, not raised as a bare metric,
rendered as the same tan hexagon check-node color used elsewhere in the
book) versus genuinely healthy and complete.
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
        "suffix": "",  # docs/diagrams/ch23-model-potpunosti.png (default locale, no suffix)
        "nodes": {
            "job": "Zakazan/batch zadatak",
            "started": "Da li je\npokrenut?",
            "alarm_not_started": "Alarm: nije ni pokušao",
            "produced_output": "Da li je\nproizveo izlaz?",
            "why_failed": "Zašto nije\nuspeo?",
            "retry": "Ponovi pokušaj",
            "alarm_no_retry": "Alarm: ne pokušavaj\nponovo",
            "zero_rows": "Alarm:\nkorak pokrenut i\nredova=0\n(spojen uslov, ne goli)",
            "healthy": "Zdravo — potpuno",
        },
        "edges": {
            "no": "ne",
            "yes": "da",
            "transient": "prolazan uzrok",
            "permanent": "trajan uzrok",
            "zero_rows": "da, ali NULA redova",
            "with_data": "da, sa podacima",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch23-model-potpunosti.en.png
        "nodes": {
            "job": "Scheduled/batch job",
            "started": "Did it\nstart?",
            "alarm_not_started": "Alarm: never even\nstarted",
            "produced_output": "Did it\nproduce output?",
            "why_failed": "Why did it\nfail?",
            "retry": "Retry",
            "alarm_no_retry": "Alarm: don't\nretry",
            "zero_rows": "Alarm:\nstep ran and\nrows=0\n(merged condition, not\nraised bare)",
            "healthy": "Healthy — complete",
        },
        "edges": {
            "no": "no",
            "yes": "yes",
            "transient": "transient cause",
            "permanent": "permanent cause",
            "zero_rows": "yes, but ZERO rows",
            "with_data": "yes, with data",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("ch23_model_potpunosti", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.45", ranksep="0.85", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("job", n["job"])
    g.node("started", n["started"], shape="diamond")
    g.node("alarm_not_started", n["alarm_not_started"])
    g.node("produced_output", n["produced_output"], shape="diamond")
    g.node("why_failed", n["why_failed"], shape="diamond")
    g.node("retry", n["retry"])
    g.node("alarm_no_retry", n["alarm_no_retry"])
    g.node("zero_rows", n["zero_rows"], shape="hexagon", fillcolor=NOTE_FILL,
           color=NOTE_LINE)
    g.node("healthy", n["healthy"], fillcolor=NOTE_FILL, color=NOTE_LINE)

    g.edge("job", "started")
    g.edge("started", "alarm_not_started", label=e["no"])
    g.edge("started", "produced_output", label=e["yes"])

    g.edge("produced_output", "why_failed", label=e["no"])
    g.edge("produced_output", "zero_rows", label=e["zero_rows"])
    g.edge("produced_output", "healthy", label=e["with_data"])

    g.edge("why_failed", "retry", label=e["transient"])
    g.edge("why_failed", "alarm_no_retry", label=e["permanent"])

    out_path = OUT_DIR / f"ch23-model-potpunosti{cfg['suffix']}.png"
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
