#!/usr/bin/env python3
"""
Source-of-truth generator for the gateway-pattern diagram used in
Poglavlje 4 / Chapter 4 (gateway).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
diagram.png was hand-built with no source file kept alongside it, so its
Serbian labels were baked into raster pixels with no way to re-render
them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/diagram.py sr   # -> docs/diagrams/diagram.png
    python3 scripts/diagrams/diagram.py en   # -> docs/diagrams/diagram.en.png
    python3 scripts/diagrams/diagram.py all  # both

Structure note: telemetry senders (long-lived services, short-lived batch
jobs, and systems that can't be instrumented directly) all target one
stable internal DNS name / load balancer, which spreads traffic across
two independent gateway instances. Only the gateway instances talk to the
cloud platform -- the single place holding cloud credentials.
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
        "suffix": "",  # docs/diagrams/diagram.png (default locale, no suffix)
        "nodes": {
            "long_lived": "Dugotrajan servis\n(OTel SDK/agent)",
            "batch_jobs": "Kratkotrajni batch\nzadaci\n(+ sidecar kolektor po\nzadatku)",
            "non_instrumentable": "Sistemi koji se ne mogu\ninstrumentirati direktno\n(baze, SaaS, klasteri)",
            "lb": "Interni load balanser\n+ stabilno DNS ime",
            "gw1": "Gateway — instanca 1",
            "gw2": "Gateway — instanca 2",
            "cloud": "Cloud observability\nplatforma",
        },
        "cluster": "Pošiljaoci telemetrije",
        "edges": {
            "long_lived_lb": "OTLP",
            "batch_lb": "OTLP",
            "non_instr_lb": "pull / push",
            "gw1_cloud": "OTLP/HTTPS, jedini\nnosilac cloud\nkredencijala",
            "gw2_cloud": "OTLP/HTTPS",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/diagram.en.png
        "nodes": {
            "long_lived": "Long-lived service\n(OTel SDK/agent)",
            "batch_jobs": "Short-lived batch\njobs\n(+ sidecar collector per\njob)",
            "non_instrumentable": "Systems that can't be\ninstrumented directly\n(databases, SaaS, clusters)",
            "lb": "Internal load balancer\n+ stable DNS name",
            "gw1": "Gateway — instance 1",
            "gw2": "Gateway — instance 2",
            "cloud": "Cloud observability\nplatform",
        },
        "cluster": "Telemetry senders",
        "edges": {
            "long_lived_lb": "OTLP",
            "batch_lb": "OTLP",
            "non_instr_lb": "pull / push",
            "gw1_cloud": "OTLP/HTTPS, sole\nholder of cloud\ncredentials",
            "gw2_cloud": "OTLP/HTTPS",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("diagram", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.45", ranksep="0.9", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    with g.subgraph(name="cluster_senders") as s:
        s.attr(label=cfg["cluster"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        s.node("long_lived", n["long_lived"])
        s.node("batch_jobs", n["batch_jobs"])
        s.node("non_instrumentable", n["non_instrumentable"])

    g.node("lb", n["lb"])
    g.node("gw1", n["gw1"])
    g.node("gw2", n["gw2"])
    g.node("cloud", n["cloud"])

    g.edge("long_lived", "lb", label=e["long_lived_lb"])
    g.edge("batch_jobs", "lb", label=e["batch_lb"])
    g.edge("non_instrumentable", "lb", label=e["non_instr_lb"])
    g.edge("lb", "gw1")
    g.edge("lb", "gw2")
    g.edge("gw1", "cloud", label=e["gw1_cloud"])
    g.edge("gw2", "cloud", label=e["gw2_cloud"])

    out_path = OUT_DIR / f"diagram{cfg['suffix']}.png"
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
