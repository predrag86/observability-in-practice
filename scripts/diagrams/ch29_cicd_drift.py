#!/usr/bin/env python3
"""
Source-of-truth generator for the two diagrams used in Poglavlje 29 /
Chapter 29 (CI/CD drift — the sidecar dropped one second apart).

Follows the same convention as scripts/diagrams/diagram.py: one
parameterized Graphviz source per diagram, so both language variants
render from the same structure instead of being baked into raster
pixels with no way to re-render them in the other language.

Usage
-----
    python3 ch29_cicd_drift.py sr   # -> docs/diagrams/ch29-*.png
    python3 ch29_cicd_drift.py en   # -> docs/diagrams/ch29-*.en.png
    python3 ch29_cicd_drift.py all  # both
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
FILL_NOTE = "#EFEBE3"
LINE_NOTE = "#8D6E63"

TEXT = {
    "sr": {
        "suffix": "",
        "timeline": {
            "title": "Registrovano sa laptopa, sekund razmaka",
            "rev7_h": ":7 — standardna\n(01:23:26 UTC)",
            "rev7_b": "cpu 4096 / mem 24576\n[app, otel-sidecar] ✅",
            "rev8_h": ":8 — LARGE\n(01:23:27 UTC)",
            "rev8_b": "cpu 8192 / mem 61440\n[app] ❌ bez sidecar-a",
            "note": "Isti inženjer, isti alat,\njedan sekund razmaka —\nznak jednog skripta ili\ncopy-paste para, ne odluke",
        },
        "pipeline": {
            "title_before": "PRE",
            "title_after": "POSLE",
            "b1": "Ručno održavan\nJSON na laptopu",
            "b2": "aws ecs\nregister-task-definition",
            "b3": "Direktno u produkciju\n— nema diff-a, nema\nrevizije, nema CI-ja",
            "a1": "Izmena u\nTerraform PR-u",
            "a2": "CI: plan-time provera\n— image + sidecar\npostoje pre plana",
            "a3": "PR review\n(\"− otel-sidecar\"\nje jedna vidljiva linija)",
            "a4": "Merge → apply\n(samo iz CI-ja)",
        },
    },
    "en": {
        "suffix": ".en",
        "timeline": {
            "title": "Registered from a laptop, one second apart",
            "rev7_h": ":7 — standard\n(01:23:26 UTC)",
            "rev7_b": "cpu 4096 / mem 24576\n[app, otel-sidecar] ✅",
            "rev8_h": ":8 — LARGE\n(01:23:27 UTC)",
            "rev8_b": "cpu 8192 / mem 61440\n[app] ❌ no sidecar",
            "note": "Same engineer, same tool,\none second apart — the\nsignature of one script or\none copy-paste pair, not\na decision",
        },
        "pipeline": {
            "title_before": "BEFORE",
            "title_after": "AFTER",
            "b1": "Hand-maintained\nJSON on a laptop",
            "b2": "aws ecs\nregister-task-definition",
            "b3": "Straight to production\n— no diff, no review,\nno CI",
            "a1": "Change in a\nTerraform PR",
            "a2": "CI: plan-time check\n— image + sidecar\nexist before the plan",
            "a3": "PR review\n(\"− otel-sidecar\"\nis one visible line)",
            "a4": "Merge → apply\n(from CI only)",
        },
    },
}


def render_timeline(lang: str):
    t = TEXT[lang]["timeline"]
    suffix = TEXT[lang]["suffix"]

    g = Digraph("ch29_timeline", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.6", ranksep="0.7", splines="spline", label=t["title"],
           labelloc="t", fontsize="16", fontcolor=INK)
    g.attr("node", fontname="DejaVu Serif", fontsize="13", margin="0.25,0.18",
           shape="box", style="rounded,filled")
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="11", arrowsize="0.7")

    g.node("rev7", f"{t['rev7_h']}\n\n{t['rev7_b']}", fillcolor=FILL_GOOD, color=LINE_GOOD)
    g.node("rev8", f"{t['rev8_h']}\n\n{t['rev8_b']}", fillcolor=FILL_BAD, color=LINE_BAD)
    g.node("note", t["note"], shape="note", fillcolor=FILL_NOTE, color=LINE_NOTE, fontsize="12")

    g.edge("rev7", "rev8", label="+1s", style="dashed")
    g.edge("rev7", "note", style="invis")
    g.edge("rev8", "note")

    out_path = OUT_DIR / f"ch29-sekund-razmaka{suffix}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g.render(outfile=str(out_path), cleanup=True)
    print(f"wrote {out_path}")


def render_pipeline(lang: str):
    t = TEXT[lang]["pipeline"]
    suffix = TEXT[lang]["suffix"]

    g = Digraph("ch29_pipeline", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.5", ranksep="0.55", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="13", margin="0.25,0.16",
           shape="box", style="rounded,filled", fillcolor=FILL_NEUTRAL, color=LINE_NEUTRAL)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="11", arrowsize="0.7")

    with g.subgraph(name="cluster_before") as c:
        c.attr(label=t["title_before"], style="rounded", color=LINE_BAD,
               fontname="DejaVu Serif", fontsize="14", fontcolor=LINE_BAD, labelloc="t")
        c.node("b1", t["b1"], fillcolor=FILL_BAD, color=LINE_BAD)
        c.node("b2", t["b2"], fillcolor=FILL_BAD, color=LINE_BAD)
        c.node("b3", t["b3"], fillcolor=FILL_BAD, color=LINE_BAD)
        c.edge("b1", "b2")
        c.edge("b2", "b3")

    with g.subgraph(name="cluster_after") as c:
        c.attr(label=t["title_after"], style="rounded", color=LINE_GOOD,
               fontname="DejaVu Serif", fontsize="14", fontcolor=LINE_GOOD, labelloc="t")
        c.node("a1", t["a1"], fillcolor=FILL_GOOD, color=LINE_GOOD)
        c.node("a2", t["a2"], fillcolor=FILL_GOOD, color=LINE_GOOD)
        c.node("a3", t["a3"], fillcolor=FILL_GOOD, color=LINE_GOOD)
        c.node("a4", t["a4"], fillcolor=FILL_GOOD, color=LINE_GOOD)
        c.edge("a1", "a2")
        c.edge("a2", "a3")
        c.edge("a3", "a4")

    out_path = OUT_DIR / f"ch29-pre-posle-cevovod{suffix}.png"
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
        render_timeline(t)
        render_pipeline(t)
