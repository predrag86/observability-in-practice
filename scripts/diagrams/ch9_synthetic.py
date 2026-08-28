#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch9-synthetic" diagram used in
Poglavlje 9 / Chapter 9 (sinteticko-pracenje / synthetic monitoring).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch9-synthetic.png was hand-built with no source file kept alongside it, so
its Serbian labels were baked into raster pixels with no way to re-render
them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch9_synthetic.py sr   # -> docs/diagrams/ch9-synthetic.png
    python3 scripts/diagrams/ch9_synthetic.py en   # -> docs/diagrams/ch9-synthetic.en.png
    python3 scripts/diagrams/ch9_synthetic.py all  # both

Structure note: three regional probes each hit the public internet
directly (bypassing the internal network/DNS/gateway entirely -- the
architectural point of the chapter) and separately report their result
back to the cloud observability platform. The crossing solid lines from
the probes to "Javni internet" / "Public internet" are deliberate --
they mirror the original hand-drawn diagram's routing, not a layout bug.
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
        "suffix": "",  # docs/diagrams/ch9-synthetic.png (default locale, no suffix)
        "nodes": {
            "independence": "Ne zavisi ni od gateway-a\nni od interne DNS zone\n(Poglavlje 7 princip)",
            "probe_a": "Proba — region A",
            "probe_b": "Proba — region B",
            "probe_c": "Proba — region C",
            "internet": "Javni internet",
            "app_endpoint": "Javni endpoint\naplikacije",
            "cloud_platform": "Cloud observability\nplatforma",
        },
        "cluster_probes": "Spoljašnje probe lokacije (više regiona)",
        "edge_http": "HTTP, zaobilazi\ninternu mrežu, DNS,\ngateway",
        "edge_result": "rezultat probe",
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch9-synthetic.en.png
        "nodes": {
            "independence": "Doesn't depend on the gateway\nor the internal DNS zone\n(Chapter 7 principle)",
            "probe_a": "Probe — region A",
            "probe_b": "Probe — region B",
            "probe_c": "Probe — region C",
            "internet": "Public internet",
            "app_endpoint": "Public application\nendpoint",
            "cloud_platform": "Cloud observability\nplatform",
        },
        "cluster_probes": "External probe locations (multiple regions)",
        "edge_http": "HTTP, bypasses\ninternal network, DNS,\ngateway",
        "edge_result": "probe result",
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]

    g = Digraph("ch9_synthetic", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.55", ranksep="0.85", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("independence", n["independence"])

    with g.subgraph(name="cluster_probes") as p:
        p.attr(label=cfg["cluster_probes"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        p.node("probe_a", n["probe_a"])
        p.node("probe_b", n["probe_b"])
        p.node("probe_c", n["probe_c"])

    g.node("internet", n["internet"])
    g.node("app_endpoint", n["app_endpoint"])
    g.node("cloud_platform", n["cloud_platform"])

    g.edge("independence", "probe_a", style="invis")

    # Crossing routing to the public internet, matching the original diagram.
    g.edge("probe_a", "internet", label=cfg["edge_http"])
    g.edge("probe_b", "internet", label=cfg["edge_http"])
    g.edge("probe_c", "internet", label=cfg["edge_http"])

    g.edge("internet", "app_endpoint")

    g.edge("probe_a", "cloud_platform", label=cfg["edge_result"])
    g.edge("probe_b", "cloud_platform", label=cfg["edge_result"])
    g.edge("probe_c", "cloud_platform", label=cfg["edge_result"])

    out_path = OUT_DIR / f"ch9-synthetic{cfg['suffix']}.png"
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
