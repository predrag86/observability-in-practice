#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch6-sidecar" diagram used in
Poglavlje 6 / Chapter 6 (sidecar).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch6-sidecar.png was hand-built with no source file kept alongside it, so
its Serbian labels were baked into raster pixels with no way to re-render
them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch6_sidecar.py sr   # -> docs/diagrams/ch6-sidecar.png
    python3 scripts/diagrams/ch6_sidecar.py en   # -> docs/diagrams/ch6-sidecar.en.png
    python3 scripts/diagrams/ch6_sidecar.py all  # both

Structure note: the main container and the sidecar collector share one
ECS/Fargate task (drawn as a cluster). The env-var injection of
service.name into the sidecar is drawn dotted -- it is the one
deliberately-manual wiring point in an otherwise automatic pipeline,
same convention as ch5-instrumentation. The main container's telemetry
into the sidecar, and the sidecar's forward to the gateway, are solid --
regular pipeline flow.
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
        "suffix": "",  # docs/diagrams/ch6-sidecar.png (default locale, no suffix)
        "nodes": {
            "main_container": "Glavni kontejner\n(batch/ETL posao)",
            "env_var": "service.name ubrizgan\nkroz env promenljivu",
            "sidecar": "Sidecar kolektor\n(ADOT, deli životni\nciklus)",
            "gateway": "Centralni gateway\n(Poglavlje 4)",
        },
        "cluster": "ECS/Fargate task (jedan zadatak = jedan pokreni-pa-nestani ciklus)",
        "edges": {
            "main_sidecar": "localhost, OTLP",
            "sidecar_gateway": "batch + flush prozor\npre gašenja zadatka",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch6-sidecar.en.png
        "nodes": {
            "main_container": "Main container\n(batch/ETL job)",
            "env_var": "service.name injected\nvia env variable",
            "sidecar": "Sidecar collector\n(ADOT, shares\nlifecycle)",
            "gateway": "Central gateway\n(Chapter 4)",
        },
        "cluster": "ECS/Fargate task (one job = one run-then-vanish cycle)",
        "edges": {
            "main_sidecar": "localhost, OTLP",
            "sidecar_gateway": "batch + flush window\nbefore job shutdown",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("ch6_sidecar", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.55", ranksep="0.65", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    with g.subgraph(name="cluster_task") as t:
        t.attr(label=cfg["cluster"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t", labeljust="l")
        t.node("main_container", n["main_container"])
        t.node("env_var", n["env_var"])
        t.node("sidecar", n["sidecar"])

    g.node("gateway", n["gateway"])

    # Regular pipeline flow (solid).
    g.edge("main_container", "sidecar", label=e["main_sidecar"])
    g.edge("sidecar", "gateway", label=e["sidecar_gateway"])

    # The one manual wiring point (dotted, per book convention).
    g.edge("env_var", "sidecar", style="dotted", constraint="false")

    out_path = OUT_DIR / f"ch6-sidecar{cfg['suffix']}.png"
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
