#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch25-linkage" diagram used in
Poglavlje 25 / Chapter 25 (privatnost-telemetriji / telemetry-privacy).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch25-linkage.png was hand-built with no source file kept alongside it, so
its Serbian labels were baked into raster pixels with no way to re-render
them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch25_linkage.py sr   # -> docs/diagrams/ch25-linkage.png
    python3 scripts/diagrams/ch25_linkage.py en   # -> docs/diagrams/ch25-linkage.en.png
    python3 scripts/diagrams/ch25_linkage.py all  # both

Structure note: this is the linkage-attack diagram (see glossary: "napad
povezivanjem" / "linkage attack"). Two boxes, each fine in isolation --
the browser's intentionally pseudonymous user.id, and the backend's real
enduser.id (a legitimate, independent decision for debugging) -- both
feed the same trace-linking context. Joining them at the trace produces
the outcome that matters: pseudonym and real identity end up in the same
record, which is trivial re-identification. The green fix note (dotted
edge into the backend box) is the chapter's actual remediation: make the
backend write the same pseudonym form instead.
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"
POS_FILL = "#E6F4EA"
POS_LINE = "#2E7D4F"
NEG_FILL = "#FDE7E7"
NEG_LINE = "#C0392B"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch25-linkage.png (default locale, no suffix)
        "nodes": {
            "fix_note": "POPRAVKA: backend\nupisuje\nisti oblik pseudonima\n(ključem-zaštićena heš\nfunkcija)",
            "user_id": "user.id = pseudonimni\nUUID\n(namerno, od početka\nispravno)",
            "enduser_id": "enduser.id = PRAVI\nIDENTITET\n(nezavisna, legitimna\nodluka\nza operativno\notklanjanje grešaka)",
            "merged_trace": "Spojen trejs",
            "final": "Pseudonim + pravi\nidentitet\nu ISTOM zapisu\n= trivijalna re-\nidentifikacija",
        },
        "clusters": {
            "browser": "Pregledač (frontend)",
            "backend": "Backend servis",
        },
        "edges": {
            "linking_context": "isti kontekst\npovezivanja trejsa",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch25-linkage.en.png
        "nodes": {
            "fix_note": "FIX: backend writes\nthe same form of\npseudonym\n(keyed hash function)",
            "user_id": "user.id = pseudonymous\nUUID\n(intentional, correct\nfrom the start)",
            "enduser_id": "enduser.id = REAL\nIDENTITY\n(independent, legitimate\ndecision\nfor operational\ndebugging)",
            "merged_trace": "Joined trace",
            "final": "Pseudonym + real\nidentity\nin the SAME record\n= trivial re-\nidentification",
        },
        "clusters": {
            "browser": "Browser (frontend)",
            "backend": "Backend service",
        },
        "edges": {
            "linking_context": "same trace-linking\ncontext",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    c = cfg["clusters"]
    e = cfg["edges"]

    g = Digraph("ch25_linkage", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.55", ranksep="0.7", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("fix_note", n["fix_note"], fillcolor=POS_FILL, color=POS_LINE)

    with g.subgraph(name="cluster_browser") as b:
        b.attr(label=c["browser"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        b.node("user_id", n["user_id"])

    with g.subgraph(name="cluster_backend") as be:
        be.attr(label=c["backend"], style="rounded", color=BOX_LINE,
                fontname="DejaVu Serif", labelloc="t")
        be.node("enduser_id", n["enduser_id"], fillcolor=NEG_FILL, color=NEG_LINE)

    g.node("merged_trace", n["merged_trace"], shape="hexagon")
    g.node("final", n["final"], shape="ellipse")

    # Keep the two source clusters side by side, above the merge point.
    with g.subgraph() as s:
        s.attr(rank="same")
        s.node("user_id")
        s.node("enduser_id")

    g.edge("fix_note", "enduser_id", style="dotted")
    g.edge("user_id", "merged_trace", label=e["linking_context"])
    g.edge("enduser_id", "merged_trace", label=e["linking_context"])
    g.edge("merged_trace", "final")

    out_path = OUT_DIR / f"ch25-linkage{cfg['suffix']}.png"
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
