#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch13-dual-path" diagram used in
Poglavlje 13 / Chapter 13 (arhitektura-alarmiranja / alerting architecture).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch13-dual-path.png was hand-built with no source file kept alongside it,
so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch13_dual_path.py sr   # -> docs/diagrams/ch13-dual-path.png
    python3 scripts/diagrams/ch13_dual_path.py en   # -> docs/diagrams/ch13-dual-path.en.png
    python3 scripts/diagrams/ch13_dual_path.py all  # both

Structure note: two independent paths (direct infrastructure events vs.
telemetry-derived signals) both converge on a single routing decision --
route by domain ownership (signal owner = channel owner). From there,
three dedicated channels are fed directly (solid edges); a fourth, dotted
edge represents the fallback case where a dedicated webhook isn't
configured yet, landing on the general, always-watched channel rather
than disappearing silently.
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
        "suffix": "",  # docs/diagrams/ch13-dual-path.png (default locale, no suffix)
        "nodes": {
            "task_state": "Promena stanja\nzadatka (pad, uspeh)",
            "classify_func": "Funkcija: klasifikuj +\ndedup + formatiraj\nporuku",
            "app_emit": "Aplikacije emituju\nmetrike/trejsove",
            "gateway": "Gateway (Poglavlje 4)",
            "cloud_platform": "Cloud platforma\n(Mimir + PromQL\nevaluacija)",
            "routing": "Rutiranje po domenu\n(vlasnik signala =\nvlasnik kanala)",
            "backend_alerts": "#backend-alerts",
            "db_alerts": "#db-alerts",
            "etl_failures": "#etl-task-failures",
            "general_channel": "opšti kanal\n(fallback, uvek gledan)",
        },
        "clusters": {
            "path_a": "Put A — direktni infrastrukturni događaji",
            "path_b": "Put B — signali izvedeni iz telemetrije",
        },
        "edges": {
            "fallback": "namenski webhook\nnepopunjen",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch13-dual-path.en.png
        "nodes": {
            "task_state": "Task state change\n(failure, success)",
            "classify_func": "Function: classify +\ndedup + format\nmessage",
            "app_emit": "Apps emit\nmetrics/traces",
            "gateway": "Gateway (Chapter 4)",
            "cloud_platform": "Cloud platform\n(Mimir + PromQL\nevaluation)",
            "routing": "Routing by domain\n(signal owner =\nchannel owner)",
            "backend_alerts": "#backend-alerts",
            "db_alerts": "#db-alerts",
            "etl_failures": "#etl-task-failures",
            "general_channel": "general channel\n(fallback, always watched)",
        },
        "clusters": {
            "path_a": "Path A — direct infrastructure events",
            "path_b": "Path B — telemetry-derived signals",
        },
        "edges": {
            "fallback": "dedicated webhook\nnot configured",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    c = cfg["clusters"]
    e = cfg["edges"]

    g = Digraph("ch13_dual_path", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.55", ranksep="0.75", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    with g.subgraph(name="cluster_path_a") as a:
        a.attr(label=c["path_a"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        a.node("task_state", n["task_state"])
        a.node("classify_func", n["classify_func"])
        a.edge("task_state", "classify_func")

    with g.subgraph(name="cluster_path_b") as b:
        b.attr(label=c["path_b"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        b.node("app_emit", n["app_emit"])
        b.node("gateway", n["gateway"])
        b.node("cloud_platform", n["cloud_platform"])
        b.edge("app_emit", "gateway")
        b.edge("gateway", "cloud_platform")

    g.node("routing", n["routing"], shape="diamond")

    g.node("backend_alerts", n["backend_alerts"])
    g.node("db_alerts", n["db_alerts"])
    g.node("etl_failures", n["etl_failures"])
    g.node("general_channel", n["general_channel"])

    # Both paths converge on the routing decision.
    g.edge("classify_func", "routing")
    g.edge("cloud_platform", "routing")

    # Dedicated routes (solid).
    g.edge("routing", "backend_alerts")
    g.edge("routing", "db_alerts")
    g.edge("routing", "etl_failures")

    # Fallback route when no dedicated webhook is configured (dotted).
    g.edge("routing", "general_channel", label=e["fallback"], style="dotted")

    out_path = OUT_DIR / f"ch13-dual-path{cfg['suffix']}.png"
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
