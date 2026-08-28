#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch10-pipeline" diagram used in
Poglavlje 10 / Chapter 10 (anatomija-pipeline / anatomy of the pipeline).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch10-pipeline.png was hand-built with no source file kept alongside it, so
its Serbian labels were baked into raster pixels with no way to re-render
them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch10_pipeline.py sr   # -> docs/diagrams/ch10-pipeline.png
    python3 scripts/diagrams/ch10_pipeline.py en   # -> docs/diagrams/ch10-pipeline.en.png
    python3 scripts/diagrams/ch10_pipeline.py all  # both

Structure note: the gateway pipeline has exactly six stations, always in
this order (the chapter's whole point is that the order is load-bearing):
receiver -> memory_limiter -> filter -> transform -> resourcedetection ->
batch -> exporter.
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
        "suffix": "",  # docs/diagrams/ch10-pipeline.png (default locale, no suffix)
        "nodes": {
            "receiver": "OTLP receiver",
            "memory_limiter": "memory_limiter\n(brana protiv pritiska)",
            "filter": "filter\n(odbaci šum)",
            "transform": "transform\n(redakcija +\nnormalizacija)",
            "resourcedetection": "resourcedetection\n(popuni što nedostaje)",
            "batch": "batch\n(grupiši)",
            "exporter": "OTLP/HTTP exporter",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch10-pipeline.en.png
        "nodes": {
            "receiver": "OTLP receiver",
            "memory_limiter": "memory_limiter\n(backpressure gate)",
            "filter": "filter\n(drop noise)",
            "transform": "transform\n(redaction +\nnormalization)",
            "resourcedetection": "resourcedetection\n(fill in what's missing)",
            "batch": "batch\n(group)",
            "exporter": "OTLP/HTTP exporter",
        },
    },
}

ORDER = [
    "receiver",
    "memory_limiter",
    "filter",
    "transform",
    "resourcedetection",
    "batch",
    "exporter",
]


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]

    g = Digraph("ch10_pipeline", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.45", ranksep="0.55", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    for key in ORDER:
        g.node(key, n[key])

    for a, b in zip(ORDER, ORDER[1:]):
        g.edge(a, b)

    out_path = OUT_DIR / f"ch10-pipeline{cfg['suffix']}.png"
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
