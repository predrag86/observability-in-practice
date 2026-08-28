#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch20-asimetrija" diagram used in
Poglavlje 20 / Chapter 20 (autentikacija-iam / authentication and IAM).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch20-asimetrija.png was hand-built with no source file kept alongside it,
so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch20_asimetrija.py sr   # -> docs/diagrams/ch20-asimetrija.png
    python3 scripts/diagrams/ch20_asimetrija.py en   # -> docs/diagrams/ch20-asimetrija.en.png
    python3 scripts/diagrams/ch20_asimetrija.py all  # both

Structure note: this is the asymmetry the chapter is about. A failed
auth event is visible by default (full detail, standard production log,
split into a low-cardinality counter and a full log line) -- the top
path. A successful auth event is invisible by default, below the
threshold that gets collected, so nothing reaches the log unless the
threshold is deliberately lowered -- the bottom path, drawn in tan since
that's the gap the chapter fixes. The dashed hexagon at the end names the
concrete security blind spots that stay unanswerable while that gap
exists.
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"
TAN_FILL = "#F4EFE6"
TAN_LINE = "#8B7355"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch20-asimetrija.png (default locale, no suffix)
        "nodes": {
            "event": "Događaj\nautentikacije",
            "outcome": "Ishod?",
            "fail_level": "Nivo: vidljiv po difoltu\n(pun detalj — ko, zašto,\nodakle)",
            "prod_log": "Standardni produkcioni\nlog",
            "low_card": "Nisko-kardinalni brojač\n(samo po realmu)",
            "full_log": "Pun log red\n(identitet + poreklo)",
            "success_level": "Nivo: NEVIDLJIV po\ndifoltu\n(ispod praga koji se\nprikuplja)",
            "nothing": "Ništa ne stiže\nbez ručnog spuštanja\npraga",
            "blind_spots": "Slepe tačke:\nnemoguće putovanje ·\nreplay tokena ·\nistovremene sesije",
        },
        "edges": {
            "outcome_fail": "Neuspeh",
            "outcome_success": "Uspeh",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch20-asimetrija.en.png
        "nodes": {
            "event": "Authentication\nevent",
            "outcome": "Outcome?",
            "fail_level": "Level: visible by default\n(full detail — who, why,\nwhere from)",
            "prod_log": "Standard production\nlog",
            "low_card": "Low-cardinality counter\n(realm only)",
            "full_log": "Full log line\n(identity + origin)",
            "success_level": "Level: INVISIBLE by\ndefault\n(below the threshold\nthat gets collected)",
            "nothing": "Nothing arrives\nwithout manually lowering\nthe threshold",
            "blind_spots": "Blind spots:\nimpossible travel ·\ntoken replay ·\nsimultaneous sessions",
        },
        "edges": {
            "outcome_fail": "Failure",
            "outcome_success": "Success",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("ch20_asimetrija", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="LR",
           nodesep="0.45", ranksep="0.7", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("event", n["event"])
    g.node("outcome", n["outcome"], shape="diamond")

    # Failure path -- visible by default (top).
    g.node("fail_level", n["fail_level"])
    g.node("prod_log", n["prod_log"])
    g.node("low_card", n["low_card"])
    g.node("full_log", n["full_log"])

    # Success path -- invisible by default (bottom), the gap this chapter fixes.
    g.node("success_level", n["success_level"], fillcolor=TAN_FILL, color=TAN_LINE)
    g.node("nothing", n["nothing"])
    g.node("blind_spots", n["blind_spots"], shape="hexagon", style="dashed",
           fillcolor="", color=BOX_LINE)

    g.edge("event", "outcome")
    g.edge("outcome", "fail_level", label=e["outcome_fail"])
    g.edge("outcome", "success_level", label=e["outcome_success"])

    g.edge("fail_level", "prod_log")
    g.edge("prod_log", "low_card")
    g.edge("prod_log", "full_log")

    g.edge("success_level", "nothing", style="dotted")
    g.edge("nothing", "blind_spots")

    out_path = OUT_DIR / f"ch20-asimetrija{cfg['suffix']}.png"
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
