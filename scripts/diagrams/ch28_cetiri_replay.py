#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch28-cetiri-replay" diagram used in
Poglavlje 28 / Chapter 28 (ai-asistirana-observability /
ai-assisted-observability).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch28-cetiri-replay.png was hand-built with no source file kept alongside
it, so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch28_cetiri_replay.py sr   # -> docs/diagrams/ch28-cetiri-replay.png
    python3 scripts/diagrams/ch28_cetiri_replay.py en   # -> docs/diagrams/ch28-cetiri-replay.en.png
    python3 scripts/diagrams/ch28_cetiri_replay.py all  # both

Structure note: four replayed incidents in parallel columns. Replay 1
and Replay 2 (gray) both converge into one green hexagon -- the agent
reached the correct diagnosis unaided. Replay 3 (gray) feeds a red
hexagon -- without the context layer a naive agent would have been
confidently wrong. Replay 4 (gray) feeds a tan hexagon -- an
automated, declared-configuration check that the agent doesn't
replace. All three hexagons converge into one bottom terminal: the
value sits in the context layer, not in tool access itself.
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"
GREEN_FILL = "#E6F4EA"
GREEN_LINE = "#2E7D4F"
RED_FILL = "#FDE7E7"
RED_LINE = "#C0392B"
NOTE_FILL = "#F4EFE6"
NOTE_LINE = "#8B7355"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch28-cetiri-replay.png (default locale, no suffix)
        "nodes": {
            "replay1": "Replay 1: Latencija\nLanac dokaza → TAČNA\ndijagnoza\n(app bug, ne infra limit)",
            "replay2": "Replay 2: Curenje\nkonekcija\nDiferencijal (dva\nokruženja?) → TAČNA\ndijagnoza\n(deljena greška u kodu)",
            "replay3": "Replay 3: Časovni\nskokovi\nBEZ konteksta →\nSAMOUVERENO\nPOGREŠNO\n(pogrešna politika\nskaliranja, ne ispad)",
            "replay4": "Replay 4: Nestali alarmi\nKlasa ODSUSTVA →\nništa ne javlja pogrešno,\nništa ne javlja UOPŠTE",
            "agent_ok": "Agent samostalno stiže\ndo tačnog odgovora",
            "context_saves": "Sloj konteksta je\nono što spašava odgovor",
            "auto_check": "Automatizovana provera\nDEKLARISANE\nkonfiguracije\ni dalje neophodna —\nagent je ne zamenjuje",
            "final": "Vrednost je u SLOJU\nKONTEKSTA,\nne u samom pristupu\nalatima",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch28-cetiri-replay.en.png
        "nodes": {
            "replay1": "Replay 1: Latency\nChain of evidence → CORRECT\ndiagnosis\n(app bug, not infra limit)",
            "replay2": "Replay 2: Connection\nleak\nDifferential (two\nenvironments?) → CORRECT\ndiagnosis\n(shared bug in the code)",
            "replay3": "Replay 3: Hourly\nspikes\nWITHOUT context →\nCONFIDENTLY\nWRONG\n(misconfigured scaling\npolicy, not an outage)",
            "replay4": "Replay 4: Missing alerts\nClass of ABSENCE →\nnothing reports incorrectly,\nnothing reports AT ALL",
            "agent_ok": "Agent independently reaches\nthe correct answer",
            "context_saves": "The context layer is\nwhat saves the answer",
            "auto_check": "Automated check of\nDECLARED\nconfiguration\nremains necessary —\nthe agent doesn't replace it",
            "final": "The value is in the CONTEXT\nLAYER,\nnot in tool access\nitself",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]

    g = Digraph("ch28_cetiri_replay", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.5", ranksep="0.65", splines="curved")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    with g.subgraph(name="rank_top") as top:
        top.attr(rank="same")
        top.node("replay1", n["replay1"])
        top.node("replay2", n["replay2"])
        top.node("replay3", n["replay3"])
        top.node("replay4", n["replay4"])

    with g.subgraph(name="rank_mid") as mid:
        mid.attr(rank="same")
        mid.node("agent_ok", n["agent_ok"], shape="hexagon",
                  fillcolor=GREEN_FILL, color=GREEN_LINE)
        mid.node("context_saves", n["context_saves"], shape="hexagon",
                  fillcolor=RED_FILL, color=RED_LINE)
        mid.node("auto_check", n["auto_check"], shape="hexagon",
                  fillcolor=NOTE_FILL, color=NOTE_LINE)

    g.node("final", n["final"], shape="box", style="rounded,filled",
           fillcolor="white", color=BOX_LINE)

    g.edge("replay1", "agent_ok")
    g.edge("replay2", "agent_ok")
    g.edge("replay3", "context_saves")
    g.edge("replay4", "auto_check")

    g.edge("agent_ok", "final")
    g.edge("context_saves", "final")
    g.edge("auto_check", "final")

    out_path = OUT_DIR / f"ch28-cetiri-replay{cfg['suffix']}.png"
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
