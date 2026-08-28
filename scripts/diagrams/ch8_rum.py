#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch8-rum" diagram used in Poglavlje 8 /
Chapter 8 (frontend-rum).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch8-rum.png was hand-built with no source file kept alongside it, so its
Serbian labels were baked into raster pixels with no way to re-render
them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch8_rum.py sr   # -> docs/diagrams/ch8-rum.png
    python3 scripts/diagrams/ch8_rum.py en   # -> docs/diagrams/ch8-rum.en.png
    python3 scripts/diagrams/ch8_rum.py all  # both

Structure note: this is the chapter's central point, drawn deliberately.
There are TWO separate PII-cleanup points (dotted arrows into the
browser) because RUM traces travel a structurally independent path from
every other "native" signal (logs, measurements, errors) -- a redaction
function guarding one does not guard the other. Backend telemetry still
goes through the gateway (dotted OTLP legs, matching the observing-side
convention from overview.py); RUM telemetry from the browser bypasses
the gateway entirely and goes straight to the hosted collector (solid,
since -- structurally -- it is the browser's own direct traffic, not a
forwarded OTLP hop).
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
        "suffix": "",  # docs/diagrams/ch8-rum.png (default locale, no suffix)
        "nodes": {
            "pii_function": "Centralna PII funkcija\n(štiti native signale:\nlogove, merenja,\ngreške)",
            "span_processor": "Zaseban span-processor\n(štiti trejsove —\ndrugi, nezavisan put!)",
            "browser": "Browser korisnika",
            "backend": "Backend servis",
            "gateway": "Gateway\n(nedostupan browseru)",
            "rum_collector": "Hostovan RUM kolektor\n(Grafana Cloud)",
        },
        "edges": {
            "browser_backend": "klik → fetch/XHR\n+ trace-context header",
            "backend_gateway": "OTLP",
            "gateway_collector": "OTLP",
            "browser_collector": (
                "RUM SDK: Core Web\nVitals,\ngreške, trejsovi (isti\n"
                "trace ID)\n— direktno, ne kroz\ngateway"
            ),
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch8-rum.en.png
        "nodes": {
            "pii_function": "Central PII function\n(protects native signals:\nlogs, measurements,\nerrors)",
            "span_processor": "Separate span processor\n(protects traces —\na different, independent path!)",
            "browser": "User's browser",
            "backend": "Backend service",
            "gateway": "Gateway\n(unreachable from browser)",
            "rum_collector": "Hosted RUM collector\n(Grafana Cloud)",
        },
        "edges": {
            "browser_backend": "click → fetch/XHR\n+ trace-context header",
            "backend_gateway": "OTLP",
            "gateway_collector": "OTLP",
            "browser_collector": (
                "RUM SDK: Core Web\nVitals,\nerrors, traces (same\n"
                "trace ID)\n— direct, not through\nthe gateway"
            ),
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("ch8_rum", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.6", ranksep="0.65", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("pii_function", n["pii_function"])
    g.node("span_processor", n["span_processor"])
    g.node("browser", n["browser"])
    g.node("backend", n["backend"])
    g.node("gateway", n["gateway"])
    g.node("rum_collector", n["rum_collector"])

    # Two independent PII-cleanup points, both feeding the browser
    # (dotted -- the point of the chapter: they guard different paths).
    g.edge("pii_function", "browser", style="dotted")
    g.edge("span_processor", "browser", style="dotted")

    # Regular application traffic (solid).
    g.edge("browser", "backend", label=e["browser_backend"])

    # Backend telemetry still goes through the gateway (dotted OTLP legs).
    g.edge("backend", "gateway", label=e["backend_gateway"], style="dotted")
    g.edge("gateway", "rum_collector", label=e["gateway_collector"], style="dotted")

    # RUM telemetry: direct from the browser, bypassing the gateway (solid).
    g.edge("browser", "rum_collector", label=e["browser_collector"])

    out_path = OUT_DIR / f"ch8-rum{cfg['suffix']}.png"
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
