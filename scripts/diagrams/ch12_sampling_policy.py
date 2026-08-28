#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch12-sampling-policy" diagram used in
Poglavlje 12 / Chapter 12 (sampling-trejsova / trace sampling).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch12-sampling-policy.png was hand-built with no source file kept alongside
it, so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch12_sampling_policy.py sr   # -> docs/diagrams/ch12-sampling-policy.png
    python3 scripts/diagrams/ch12_sampling_policy.py en   # -> docs/diagrams/ch12-sampling-policy.en.png
    python3 scripts/diagrams/ch12_sampling_policy.py all  # both

Structure note: this is a tall decision tree (rankdir="TB", matching the
original's portrait aspect ratio), not a wide left-to-right flow. Drop
policies are an absolute veto and are evaluated first; keep policies are
OR'd together with an effectively random evaluation order; only if neither
decides does the base probabilistic rate get a say. The "kept" terminal
node has two converging incoming edges (from the keep-policy check and
from a probabilistic hit), matching the original diagram.
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
        "suffix": "",  # docs/diagrams/ch12-sampling-policy.png (default locale, no suffix)
        "nodes": {
            "start": "Kompletan trejs\nsakupljen",
            "drop_check": "Zadovoljava li bilo koju\nDROP politiku?",
            "dropped_immediately": "Odbačen odmah\n(apsolutan veto)",
            "keep_check": (
                "Zadovoljava li BILO KOJU\nKEEP politiku?\n"
                "(greška / spor /\nanomalija)\n"
                "redosled evaluacije\nnasumičan"
            ),
            "kept": "Zadržan",
            "base_rate": "Bazna probabilistička\nstopa (10%)",
            "dropped_available": "Odbačen\n(dostupan 24č po trace\nID-ju)",
        },
        "edges": {
            "yes": "da",
            "no": "ne",
            "yes_at_least_one": "da, bar jedna",
            "hit": "pogodak",
            "miss": "promašaj",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch12-sampling-policy.en.png
        "nodes": {
            "start": "Complete trace\ncollected",
            "drop_check": "Does it satisfy any\nDROP policy?",
            "dropped_immediately": "Dropped immediately\n(absolute veto)",
            "keep_check": (
                "Does it satisfy ANY\nKEEP policy?\n"
                "(error / slow /\nanomaly)\n"
                "evaluation order\nrandom"
            ),
            "kept": "Retained",
            "base_rate": "Base probabilistic\nrate (10%)",
            "dropped_available": "Dropped\n(available for 24h by\ntrace ID)",
        },
        "edges": {
            "yes": "yes",
            "no": "no",
            "yes_at_least_one": "yes, at least one",
            "hit": "hit",
            "miss": "miss",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("ch12_sampling_policy", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.6", ranksep="0.65", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("start", n["start"], shape="box")
    g.node("drop_check", n["drop_check"], shape="diamond")
    g.node("dropped_immediately", n["dropped_immediately"], shape="box")
    g.node("keep_check", n["keep_check"], shape="diamond")
    g.node("kept", n["kept"], shape="box")
    g.node("base_rate", n["base_rate"], shape="diamond")
    g.node("dropped_available", n["dropped_available"], shape="box")

    g.edge("start", "drop_check")
    g.edge("drop_check", "dropped_immediately", label=e["yes"])
    g.edge("drop_check", "keep_check", label=e["no"])
    g.edge("keep_check", "kept", label=e["yes_at_least_one"])
    g.edge("keep_check", "base_rate", label=e["no"])
    g.edge("base_rate", "kept", label=e["hit"])
    g.edge("base_rate", "dropped_available", label=e["miss"])

    out_path = OUT_DIR / f"ch12-sampling-policy{cfg['suffix']}.png"
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
