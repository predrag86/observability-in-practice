#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch29-vremenska-linija" diagram used in
Poglavlje 29 / Chapter 29 (fazni-rollout / phased-rollout).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch29-vremenska-linija.png was hand-built with no source file kept
alongside it, so its Serbian labels were baked into raster pixels with no
way to re-render them in English. This script reconstructs the diagram
from one parameterized Graphviz source, so both language variants come
from the same structure.

Usage
-----
    python3 scripts/diagrams/ch29_vremenska_linija.py sr   # -> docs/diagrams/ch29-vremenska-linija.png
    python3 scripts/diagrams/ch29_vremenska_linija.py en   # -> docs/diagrams/ch29-vremenska-linija.en.png
    python3 scripts/diagrams/ch29_vremenska_linija.py all  # both

Structure note: a top-to-bottom timeline in four horizontal rows,
using the book's standard color coding (gray = neutral event, red =
problem/red-flag, tan = decision/policy note, green = resolution).
Row 1: the plan hits reality -- a race condition the "zero rows" alert
(red) never caught, so two new steps get inserted. Row 2: a deliberate
reorder decision (tan) is followed by the alert mechanism itself
turning out structurally wrong (red), replaced wholesale (gray), with
the "most critical fleet member always last" policy written down (tan).
Row 3: an audit before shutdown (gray hexagon) finds most of the old
alerts silently dead (red), so the shutdown removes a facade rather
than active protection (green).
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"
RED_FILL = "#FDE7E7"
RED_LINE = "#C0392B"
NOTE_FILL = "#F4EFE6"
NOTE_LINE = "#8B7355"
GREEN_FILL = "#E6F4EA"
GREEN_LINE = "#2E7D4F"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch29-vremenska-linija.png (default locale, no suffix)
        "nodes": {
            "plan": "Numerisan plan,\nobjavljen unapred",
            "provera": "Prva produkciona\nprovera:\n5 od 6 zadataka\ntiho pukne na trci",
            "alarm_zelen": "Alarm OSTAJE ZELEN\n—\ndelimičan upis\nzadovoljava 'nije prazno'",
            "dva_koraka": "Ubačena 2 nova koraka:\ngrub alarm + popravka\nuzroka trke",
            "odluka": "ODLUKA: pilot bočnog\nkolektora premešten\nISPRED\npopravke, prošireno na\ndve porodice",
            "prava_poruka": "Prva prava poruka\nalarma:\nmehanizam\nSTRUKTURNO\npogrešan, ne samo\nloše podešen",
            "mehanizam": "Ceo mehanizam\nzamenjen:\ndogađaj-vođen, po-\nzadatku,\ntri nivoa hitnosti",
            "politika": "Politika zapisana\nunapred:\nnajkritičniji deo sistema\nUVEK poslednji",
            "revizija": "Revizija PRE gašenja\nstarog sistema",
            "stari_alarmi": "16 od ~23 starih\nalarma:\nNULA podataka godinu\ndana\n(tiho mrtvi, izgledali\n'zeleno')",
            "ugasen": "Stari sistem ugašen —\nne brisanje zaštite,\nnego uklanjanje fasade",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch29-vremenska-linija.en.png
        "nodes": {
            "plan": "Numbered plan,\npublished ahead of time",
            "provera": "First production\ncheck:\n5 of 6 tasks\ncrash silently on a race",
            "alarm_zelen": "Alert STAYS GREEN\n—\na partial write\nsatisfies 'not empty'",
            "dva_koraka": "2 new steps inserted:\ncoarse alert + fix for\nthe race cause",
            "odluka": "DECISION: sidecar\ncollector pilot moved\nAHEAD\nof the fix, expanded to\ntwo families",
            "prava_poruka": "First real alert\nmessage:\nmechanism\nSTRUCTURALLY\nwrong, not just\npoorly tuned",
            "mehanizam": "Whole mechanism\nreplaced:\nevent-driven, per-\ntask,\nthree urgency tiers",
            "politika": "Policy written down\nin advance:\nmost critical part of the\nsystem ALWAYS last",
            "revizija": "Audit BEFORE shutting\ndown the old system",
            "stari_alarmi": "16 of ~23 old\nalerts:\nZERO data points in a\nyear\n(silently dead, looked\n'green')",
            "ugasen": "Old system shut down —\nnot deleting protection,\nbut removing a facade",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]

    g = Digraph("ch29_vremenska_linija", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.45", ranksep="0.7", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    # -- Row 1: reality exposes the gap the alert didn't catch ----------
    with g.subgraph(name="row1") as r:
        r.attr(rank="same")
        r.node("plan", n["plan"])
        r.node("provera", n["provera"])
        r.node("alarm_zelen", n["alarm_zelen"], fillcolor=RED_FILL, color=RED_LINE)
        r.node("dva_koraka", n["dva_koraka"])
    g.edge("plan", "provera")
    g.edge("provera", "alarm_zelen")
    g.edge("alarm_zelen", "dva_koraka")

    # -- Row 2: reorder decision, then the mechanism itself replaced ----
    with g.subgraph(name="row2") as r:
        r.attr(rank="same")
        r.node("odluka", n["odluka"], fillcolor=NOTE_FILL, color=NOTE_LINE)
        r.node("prava_poruka", n["prava_poruka"], fillcolor=RED_FILL, color=RED_LINE)
        r.node("mehanizam", n["mehanizam"])
        r.node("politika", n["politika"], fillcolor=NOTE_FILL, color=NOTE_LINE)
    g.edge("odluka", "prava_poruka")
    g.edge("prava_poruka", "mehanizam")
    g.edge("mehanizam", "politika")
    g.edge("dva_koraka", "odluka")

    # -- Row 3: audit before shutdown ------------------------------------
    with g.subgraph(name="row3") as r:
        r.attr(rank="same")
        r.node("revizija", n["revizija"], shape="hexagon",
               fillcolor=BOX_FILL, color=BOX_LINE)
        r.node("stari_alarmi", n["stari_alarmi"], fillcolor=RED_FILL, color=RED_LINE)
        r.node("ugasen", n["ugasen"], shape="ellipse",
               fillcolor=GREEN_FILL, color=GREEN_LINE)
    g.edge("revizija", "stari_alarmi")
    g.edge("stari_alarmi", "ugasen")
    g.edge("politika", "revizija")

    out_path = OUT_DIR / f"ch29-vremenska-linija{cfg['suffix']}.png"
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
