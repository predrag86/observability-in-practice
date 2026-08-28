#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch19-trostruki-signal" diagram used in
Poglavlje 19 / Chapter 19 (samostalni-klaster / self-managed cluster).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch19-trostruki-signal.png was hand-built with no source file kept
alongside it, so its Serbian labels were baked into raster pixels with no
way to re-render them in English. This script reconstructs the diagram
from one parameterized Graphviz source, so both language variants come
from the same structure.

Usage
-----
    python3 scripts/diagrams/ch19_trostruki_signal.py sr   # -> docs/diagrams/ch19-trostruki-signal.png
    python3 scripts/diagrams/ch19_trostruki_signal.py en   # -> docs/diagrams/ch19-trostruki-signal.en.png
    python3 scripts/diagrams/ch19_trostruki_signal.py all  # both

Structure note: each cluster node carries three independent signals (host,
log, JVM/application) -- the JVM layer is called out in tan because,
unlike the other two, a change there means a process restart. Below that,
the "blast radius of the change?" decision drives a strict three-step
rollout ordered by increasing blast radius: executor node #1 (canary),
executor node #2 (confirmation), and the coordinator node last, since a
coordinator failure stops the whole cluster. Separately, before any new
node-level metrics source is turned on, its cardinality cost is checked
first (dotted edge into the hexagon) -- the cost that, unchecked, doubled
the cluster's active series in the real incident this chapter describes.
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"
TAN_FILL = "#F4EFE6"
TAN_LINE = "#8B7355"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch19-trostruki-signal.png (default locale, no suffix)
        "nodes": {
            "host_layer": "Host sloj\nCPU · memorija · disk\n(bez restarta procesa)",
            "log_layer": "Log sloj\ngreške · upozorenja\n(bez restarta procesa)",
            "jvm_layer": "JVM/aplikativni sloj\nheap · GC pauze · red\nčekanja\n(promena = restart\nprocesa)",
            "decision": "Radijus dejstva\npromene?",
            "exec1": "Izvršni čvor #1",
            "exec2": "2. Izvršni čvor #2\n(potvrda)",
            "coordinator": "3. Koordinacioni čvor\n(poslednji — pad\nzaustavlja sve)",
            "cardinality_check": "Budžet kardinalnosti\nproveren PRE\nuključivanja\nnovog JMX/Dropwizard\nizvora",
        },
        "clusters": {
            "node": "Jedan čvor klastera",
        },
        "edges": {
            "decision_exec1": "1. izvršni čvor (canary)",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch19-trostruki-signal.en.png
        "nodes": {
            "host_layer": "Host layer\nCPU · memory · disk\n(no process restart)",
            "log_layer": "Log layer\nerrors · warnings\n(no process restart)",
            "jvm_layer": "JVM/application layer\nheap · GC pauses · queue\ndepth\n(change = process\nrestart)",
            "decision": "Blast radius\nof the change?",
            "exec1": "Executor node #1",
            "exec2": "2. Executor node #2\n(confirmation)",
            "coordinator": "3. Coordinator node\n(last — a failure\nstops everything)",
            "cardinality_check": "Cardinality budget\nchecked BEFORE\nturning on a new\nJMX/Dropwizard source",
        },
        "clusters": {
            "node": "One cluster node",
        },
        "edges": {
            "decision_exec1": "1. executor node (canary)",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    c = cfg["clusters"]
    e = cfg["edges"]

    g = Digraph("ch19_trostruki_signal", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.5", ranksep="0.7", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    with g.subgraph(name="cluster_node") as node:
        node.attr(label=c["node"], style="rounded", color=BOX_LINE,
                  fontname="DejaVu Serif", labelloc="t")
        # rank=same keeps the three signal boxes in one row, matching the
        # original's side-by-side layout (exact left-right order among them
        # is cosmetic -- Graphviz settles it via edge-crossing minimization
        # against the decision/hexagon nodes below).
        node.attr(rank="same")
        node.node("host_layer", n["host_layer"])
        node.node("log_layer", n["log_layer"])
        node.node("jvm_layer", n["jvm_layer"], fillcolor=TAN_FILL, color=TAN_LINE)

    g.node("decision", n["decision"], shape="diamond")
    g.node("cardinality_check", n["cardinality_check"], shape="hexagon",
           style="", fillcolor="")

    g.node("exec1", n["exec1"])
    g.node("exec2", n["exec2"])
    g.node("coordinator", n["coordinator"], fillcolor=TAN_FILL, color=TAN_LINE)

    # The one manual/deliberate check before adding a new metrics source.
    g.edge("host_layer", "cardinality_check", style="dotted")

    g.edge("host_layer", "decision")
    g.edge("decision", "exec1", label=e["decision_exec1"])
    g.edge("exec1", "exec2")
    g.edge("exec2", "coordinator")

    out_path = OUT_DIR / f"ch19-trostruki-signal{cfg['suffix']}.png"
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
