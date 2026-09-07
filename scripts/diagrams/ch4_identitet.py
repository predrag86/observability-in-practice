#!/usr/bin/env python3
"""
Source-of-truth generator for the "popuni, ne prepiši" / gateway-identity-leak
diagram used in Poglavlje 4 (gateway), matching the real, single-stage fix
(a narrow strip-step for one sender, right after resourcedetection) rather
than the earlier, inaccurate two-stage telling this replaces.

Follows the same convention as scripts/diagrams/ch6_taskdef_drift.py.

Usage
-----
    python3 ch4_identitet.py sr   # -> docs/diagrams/ch04-identitet-popuni-ako-nedostaje.png
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
        "title": "Popravka je uzak korak za jednog pošiljaoca, ne premeštanje mehanizma",
        "sender_x": "Pošiljalac X\n(ne postavlja sopstvene\nresursne atribute)",
        "sender_other": "Svi ostali pošiljaoci",
        "rd": "resourcedetection\npopuni AKO NEDOSTAJE\n(override=false)",
        "gw_id": "Sopstveni identitet gateway-a\n(zona, zadatak, tip izvršavanja)",
        "leak": "popunjava prazninu\nidentitetom gateway-a",
        "strip": "NOVO: strip_gateway_identity\nuzak filter, samo za pošiljaoca X\n(briše tih 8 atributa po imenu servisa)",
        "export": "batch → export",
        "note": "Svi ostali pošiljaoci prolaze kroz\nisti korak nedirnuto — filter cilja\nsamo pošiljaoca X, ne menja mehanizam\nza sve.",
    },
    "en": {
        "suffix": ".en",
        "title": "The fix is a narrow step for one sender, not a relocation of the mechanism",
        "sender_x": "Sender X\n(sets no resource\nattributes of its own)",
        "sender_other": "Every other sender",
        "rd": "resourcedetection\nfill IF MISSING\n(override=false)",
        "gw_id": "Gateway's own identity\n(zone, task, launch type)",
        "leak": "fills the gap with\nthe gateway's identity",
        "strip": "NEW: strip_gateway_identity\nnarrow filter, sender X only\n(deletes those 8 attributes by service name)",
        "export": "batch → export",
        "note": "Every other sender passes through\nthe same step untouched — the filter\ntargets sender X only, it doesn't\nchange the mechanism for everyone.",
    },
}


def build(lang: str) -> Digraph:
    t = TEXT[lang]
    g = Digraph("ch04_identitet", format="png")
    g.attr(
        rankdir="TB",
        bgcolor="white",
        fontname="Helvetica",
        fontcolor=INK,
        label=t["title"],
        labelloc="t",
        fontsize="16",
        pad="0.3",
        nodesep="0.4",
        ranksep="0.45",
    )
    g.attr(
        "node",
        fontname="Helvetica",
        fontcolor=INK,
        shape="box",
        style="filled,rounded",
        color=LINE_NEUTRAL,
        fillcolor=FILL_NEUTRAL,
        fontsize="12",
        margin="0.18,0.12",
    )
    g.attr("edge", color=LINE_NEUTRAL, fontname="Helvetica", fontsize="11", fontcolor=INK)

    g.node("sender_x", t["sender_x"])
    g.node("sender_other", t["sender_other"])
    g.node("gw_id", t["gw_id"], fillcolor=FILL_BAD, color=LINE_BAD)
    g.node("rd", t["rd"])
    g.node("strip", t["strip"], fillcolor=FILL_GOOD, color=LINE_GOOD)
    g.node("export", t["export"])
    g.node("note", t["note"], shape="note", fillcolor="white", fontsize="10")

    g.edge("sender_x", "rd")
    g.edge("sender_other", "rd")
    g.edge("gw_id", "rd", style="dashed", color=LINE_BAD, label=t["leak"], fontcolor=LINE_BAD)
    g.edge("rd", "strip")
    g.edge("strip", "export")
    g.edge("note", "strip", style="invis")

    return g


def main() -> None:
    langs = sys.argv[1:] or ["sr"]
    if "all" in langs:
        langs = list(TEXT.keys())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for lang in langs:
        g = build(lang)
        suffix = TEXT[lang]["suffix"]
        data = g.pipe(format="png")
        png_path = OUT_DIR / f"ch04-identitet-popuni-ako-nedostaje{suffix}.png"
        png_path.write_bytes(data)
        print(f"wrote {png_path}")


if __name__ == "__main__":
    main()
