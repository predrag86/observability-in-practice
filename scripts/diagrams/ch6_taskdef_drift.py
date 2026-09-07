#!/usr/bin/env python3
"""
Source-of-truth generator for the task-definition-drift diagram used in
Poglavlje 6 / Chapter 6 (sidecar) -- new subsection on registration vs.
pin drift.

Follows the same convention as scripts/diagrams/ch29_cicd_drift.py: one
parameterized Graphviz source per diagram, so both language variants
render from the same structure instead of being baked into raster pixels.

Usage
-----
    python3 ch6_taskdef_drift.py sr   # -> docs/diagrams/ch06-pinovi-driftuju.png
    python3 ch6_taskdef_drift.py en   # -> docs/diagrams/ch06-pinovi-driftuju.en.png
    python3 ch6_taskdef_drift.py all  # both
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
FILL_NEUTRAL = "#EEEEEE"
LINE_NEUTRAL = "#999999"
FILL_GOOD = "#E8F5E9"
LINE_GOOD = "#2E7D32"
FILL_BAD = "#FDECEA"
LINE_BAD = "#C62828"

TEXT = {
    "sr": {
        "suffix": "",
        "title": "Jedna porodica, tri nezavisne tačke lansiranja — svaka pinovana na svoju reviziju",
        "fam": "Porodica X — revizije\nregistrovane u AWS",
        "rev6": ":6\nbez sidecar-a",
        "rev7": ":7 — standardna\n[app, otel-sidecar] ✓",
        "rev8": ":8 — LARGE\n[app] ✗ bez sidecar-a\n(pao iz para sa :7)",
        "l1": "Launcher A\n(env promenljiva, pin :7)",
        "l2": "Launcher B\n(hardkodovano u kodu, pin :8)",
        "l3": "EventBridge pravilo\n(bez broja revizije\n→ auto-latest)",
        "note": "Registrovanje nove revizije ne\nažurira nijedan pin automatski —\nsvaka tačka lansiranja ostaje na\nreviziji na koju je poslednji put\neksplicitno pokazana.",
    },
    "en": {
        "suffix": ".en",
        "title": "One family, three independent launch points — each pinned to its own revision",
        "fam": "Family X — revisions\nregistered in AWS",
        "rev6": ":6\nno sidecar",
        "rev7": ":7 — standard\n[app, otel-sidecar] ✓",
        "rev8": ":8 — LARGE\n[app] ✗ no sidecar\n(dropped from the :7 pair)",
        "l1": "Launcher A\n(env variable, pinned :7)",
        "l2": "Launcher B\n(hardcoded in code, pinned :8)",
        "l3": "EventBridge rule\n(no revision number\n→ auto-latest)",
        "note": "Registering a new revision updates\nno pin automatically — every launch\npoint stays on whatever revision it\nwas last explicitly pointed at.",
    },
}


def render(lang: str):
    t = TEXT[lang]
    suffix = t["suffix"]

    g = Digraph("ch6_taskdef_drift", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.55", ranksep="0.75", splines="spline",
           label=t["title"], labelloc="t", fontsize="15", fontcolor=INK)
    g.attr("node", fontname="DejaVu Serif", fontsize="12", margin="0.22,0.16",
           shape="box", style="rounded,filled")
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="11", arrowsize="0.7")

    with g.subgraph(name="cluster_fam") as c:
        c.attr(label=t["fam"], style="rounded", color=LINE_NEUTRAL,
               fontname="DejaVu Serif", fontsize="13", fontcolor=INK, labelloc="t")
        c.node("rev6", t["rev6"], fillcolor=FILL_BAD, color=LINE_BAD)
        c.node("rev7", t["rev7"], fillcolor=FILL_GOOD, color=LINE_GOOD)
        c.node("rev8", t["rev8"], fillcolor=FILL_BAD, color=LINE_BAD)
        c.edge("rev6", "rev7", style="invis")
        c.edge("rev7", "rev8", style="invis")

    g.node("l1", t["l1"], fillcolor=FILL_NEUTRAL, color=LINE_NEUTRAL)
    g.node("l2", t["l2"], fillcolor=FILL_NEUTRAL, color=LINE_NEUTRAL)
    g.node("l3", t["l3"], fillcolor=FILL_NEUTRAL, color=LINE_NEUTRAL)
    g.node("note", t["note"], shape="note", fillcolor="#EFEBE3", color="#8D6E63", fontsize="11")

    g.edge("l1", "rev7", color=LINE_GOOD)
    g.edge("l2", "rev8", color=LINE_BAD)
    g.edge("l3", "rev8", color=LINE_BAD, style="dashed", label="latest")
    g.edge("rev8", "note", style="invis")

    out_path = OUT_DIR / f"ch06-pinovi-driftuju{suffix}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g.render(outfile=str(out_path), cleanup=True)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    targets = sys.argv[1:] or ["en"]
    if targets == ["all"]:
        targets = list(TEXT.keys())
    for t in targets:
        if t not in TEXT:
            raise SystemExit(f"unknown language {t!r}, known: {list(TEXT)}")
        render(t)
