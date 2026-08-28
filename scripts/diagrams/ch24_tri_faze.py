#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch24-tri-faze" diagram used in
Poglavlje 24 / Chapter 24 (snowflake-servis-koji-nije-nas /
snowflake-a-service-that-isnt-ours).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch24-tri-faze.png was hand-built with no source file kept alongside it, so
its Serbian labels were baked into raster pixels with no way to re-render
them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch24_tri_faze.py sr   # -> docs/diagrams/ch24-tri-faze.png
    python3 scripts/diagrams/ch24_tri_faze.py en   # -> docs/diagrams/ch24-tri-faze.en.png
    python3 scripts/diagrams/ch24_tri_faze.py all  # both

Structure note: one scheduled run fans out into three collection phases
that all share the same short-lived session (dotted edges into the
"same session" note -- that sharing is what keeps the extra cost near
zero above Phase 1). Phase 3 also feeds a freshness metric, which -- along
with an independent collector-health metric -- feeds the staleness alert.
That alert is deliberately drawn with two distinct outcomes: a dead
collector must never be read as a real data-flow outage, so "collector
dead" routes to an explicit "no condition = false catastrophe" note,
while "collector alive, data actually stale" routes to a genuine outage
node.
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
        "suffix": "",  # docs/diagrams/ch24-tri-faze.png (default locale, no suffix)
        "nodes": {
            "schedule": "Zakazano pokretanje\n(jedna kratka sesija)",
            "phase1": "Faza 1\nnajsporiji upiti → logovi",
            "phase2": "Faza 2\nmetrike naloga →\nmetrike platforme",
            "phase3": "Faza 3\nsvežina + agregati\nupita → metrike\nplatforme",
            "same_session": "Ista sesija za sve tri faze\n= ~0 dodatnih kredita\niznad Faze 1",
            "freshness": "Metrika svežine\npodataka",
            "collector_alive": "Metrika: da li je\nkolektor živ?",
            "alarm": "Alarm o zastarelosti",
            "false_alarm": "BEZ uslova: lažna\n'katastrofa' na zdravom\nsistemu",
            "real_outage": "Stvaran prekid dotoka",
        },
        "edges": {
            "collector_dead": "kolektor mrtav",
            "collector_alive_stale": "kolektor živ, podatak\nstar",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch24-tri-faze.en.png
        "nodes": {
            "schedule": "Scheduled run\n(one short session)",
            "phase1": "Phase 1\nslowest queries → logs",
            "phase2": "Phase 2\naccount metrics →\nplatform metrics",
            "phase3": "Phase 3\nfreshness + query\naggregates → platform\nmetrics",
            "same_session": "Same session for all three\nphases = ~0 extra credits\nabove Phase 1",
            "freshness": "Data freshness\nmetric",
            "collector_alive": "Metric: is the\ncollector alive?",
            "alarm": "Staleness alert",
            "false_alarm": "NO condition: false\n'catastrophe' on a healthy\nsystem",
            "real_outage": "Actual data-flow outage",
        },
        "edges": {
            "collector_dead": "collector dead",
            "collector_alive_stale": "collector alive, data\nstale",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("ch24_tri_faze", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.5", ranksep="0.75", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("schedule", n["schedule"])
    g.node("phase1", n["phase1"])
    g.node("phase2", n["phase2"])
    g.node("phase3", n["phase3"])
    g.node("same_session", n["same_session"], shape="hexagon",
           fillcolor=NOTE_FILL, color=NOTE_LINE)
    g.node("freshness", n["freshness"])
    g.node("collector_alive", n["collector_alive"])
    g.node("alarm", n["alarm"], shape="diamond")
    g.node("false_alarm", n["false_alarm"], style="filled,dashed",
           fillcolor=NOTE_FILL, color=NOTE_LINE)
    g.node("real_outage", n["real_outage"], style="filled",
           fillcolor="white", color="#333333")

    # Keep the three phases on one rank, side by side.
    with g.subgraph() as s:
        s.attr(rank="same")
        s.node("phase1")
        s.node("phase2")
        s.node("phase3")

    with g.subgraph() as s:
        s.attr(rank="same")
        s.node("freshness")
        s.node("collector_alive")

    with g.subgraph() as s:
        s.attr(rank="same")
        s.node("false_alarm")
        s.node("real_outage")

    g.edge("schedule", "phase1")
    g.edge("schedule", "phase2")
    g.edge("schedule", "phase3")

    g.edge("phase1", "same_session", style="dotted")
    g.edge("phase2", "same_session", style="dotted")
    g.edge("phase3", "same_session", style="dotted")

    g.edge("phase3", "freshness")
    g.edge("freshness", "alarm")
    g.edge("collector_alive", "alarm", style="dotted")

    g.edge("alarm", "false_alarm", label=e["collector_dead"])
    g.edge("alarm", "real_outage", label=e["collector_alive_stale"])

    out_path = OUT_DIR / f"ch24-tri-faze{cfg['suffix']}.png"
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
