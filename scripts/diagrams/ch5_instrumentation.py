#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch5-instrumentation" diagram used in
Poglavlje 5 / Chapter 5 (instrumentacija / instrumentation).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch5-instrumentation.png was hand-built with no source file kept alongside
it, so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch5_instrumentation.py sr   # -> docs/diagrams/ch5-instrumentation.png
    python3 scripts/diagrams/ch5_instrumentation.py en   # -> docs/diagrams/ch5-instrumentation.en.png
    python3 scripts/diagrams/ch5_instrumentation.py all  # both

Structure note: auto-instrumentation (Java agent, Python entrypoint
shim/SDK) feeds the shared middleware layer with solid edges (it just
works, no manual wiring needed downstream of it); the three identity
sources that require manual extraction (UI session token, API key,
legacy query param) feed it with dotted edges -- these are the one
deliberately-maintained manual instrumentation point in the whole
system.
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
        "suffix": "",  # docs/diagrams/ch5-instrumentation.png (default locale, no suffix)
        "nodes": {
            "java_agent": "Auto-instrumentacioni\nagent (-javaagent)",
            "python_shim": "Entrypoint shim\n+ SDK setup",
            "ui_token": "UI sesijski token",
            "api_key": "API ključ",
            "legacy_param": "Legacy query-param",
            "middleware": "Zajednički middleware\nsloj\n(jedina ručna tačka:\nekstrakcija identiteta\npozivaoca)",
            "otlp": "OTLP",
            "gateway": "Gateway\n(Poglavlje 4)",
        },
        "clusters": {
            "java": "Java servis",
            "python": "Python servis",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch5-instrumentation.en.png
        "nodes": {
            "java_agent": "Auto-instrumentation\nagent (-javaagent)",
            "python_shim": "Entrypoint shim\n+ SDK setup",
            "ui_token": "UI session token",
            "api_key": "API key",
            "legacy_param": "Legacy query param",
            "middleware": "Shared middleware\nlayer\n(the only manual point:\ncaller identity\nextraction)",
            "otlp": "OTLP",
            "gateway": "Gateway\n(Chapter 4)",
        },
        "clusters": {
            "java": "Java service",
            "python": "Python service",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    c = cfg["clusters"]

    g = Digraph("ch5_instrumentation", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.45", ranksep="0.85", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    with g.subgraph(name="cluster_java") as j:
        j.attr(label=c["java"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        j.node("java_agent", n["java_agent"])

    with g.subgraph(name="cluster_python") as p:
        p.attr(label=c["python"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        p.node("python_shim", n["python_shim"])

    g.node("ui_token", n["ui_token"])
    g.node("api_key", n["api_key"])
    g.node("legacy_param", n["legacy_param"])
    g.node("middleware", n["middleware"])
    g.node("otlp", n["otlp"])
    g.node("gateway", n["gateway"])

    # Auto-instrumentation feeds the middleware automatically (solid).
    g.edge("java_agent", "middleware")
    g.edge("python_shim", "middleware")

    # The three manual identity sources (dotted -- the one manual point).
    g.edge("ui_token", "middleware", style="dotted")
    g.edge("api_key", "middleware", style="dotted")
    g.edge("legacy_param", "middleware", style="dotted")

    g.edge("middleware", "otlp")
    g.edge("otlp", "gateway")

    out_path = OUT_DIR / f"ch5-instrumentation{cfg['suffix']}.png"
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
