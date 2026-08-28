#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch30-ciklus-revizije" diagram used in
Poglavlje 30 / Chapter 30 (merenje-zrelosti / measuring-maturity).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch30-ciklus-revizije.png was hand-built with no source file kept
alongside it, so its Serbian labels were baked into raster pixels with
no way to re-render them in English. This script reconstructs the
diagram from one parameterized Graphviz source, so both language
variants come from the same structure.

Usage
-----
    python3 scripts/diagrams/ch30_ciklus_revizije.py sr   # -> docs/diagrams/ch30-ciklus-revizije.png
    python3 scripts/diagrams/ch30_ciklus_revizije.py en   # -> docs/diagrams/ch30-ciklus-revizije.en.png
    python3 scripts/diagrams/ch30_ciklus_revizije.py all  # both

Structure note: the book's standard color coding (gray = neutral,
red = problem/red-flag, tan = decision/policy note, green not used
here). Row 1: five review passes (gray) feed a hexagon that labels
every claim's confidence (measured / from documentation / retracted).
That feeds a tan "retracted findings" section at the top of the
document, which splits into two red findings (a fix already shipped
but never verified; an alert that rang for ten weeks). Both converge
into a hexagon comparing recommendations against actual tracking,
which lands on a tan terminal: almost none of it was actually tracked.
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

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch30-ciklus-revizije.png (default locale, no suffix)
        "nodes": {
            "p1": "Prolaz 1: čitanje\ndokumentacije,\nizvlačenje tvrdnji",
            "p2": "Prolaz 2: usklađivanje\nsa sistemom za\npraćenje rada",
            "p34": "Prolaz 3+4: dva kruga\nprovere protiv\nžive platforme",
            "p5": "Prolaz 5: PONOVO\nizmeri\nSVAKU brojku —\nestate se promenio",
            "oznaka": "Svaka tvrdnja označena:\nizmereno / iz\ndokumentacije /\nopovrgnuto",
            "sekcija": "Sekcija na VRHU:\n3 nalaza povučena,\n3 tačna u pravcu,\npogrešna u iznosu",
            "suprotan": "Nalaz u suprotnom\nsmeru:\npopravka VEĆ\nugrađena,\nsamo zaboravljen\nprekidač",
            "zvoni": "Alarm koji zvoni\nNEPREKIDNO ~10\nnedelja —\nnamerno na vrhu liste",
            "poredjenje": "Poređenje: koliko\npreporuka\nje zaista u sistemu\nza praćenje rada?",
            "odgovor": "Odgovor: gotovo\nnijedna —\nnalazi postojali, ali niko\nformalno zadužen",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch30-ciklus-revizije.en.png
        "nodes": {
            "p1": "Pass 1: reading\ndocumentation,\nextracting claims",
            "p2": "Pass 2: reconciling\nwith the work-tracking\nsystem",
            "p34": "Pass 3+4: two rounds\nof checking against\nthe live platform",
            "p5": "Pass 5: RE-MEASURE\nEVERY\nnumber —\nthe estate has changed",
            "oznaka": "Every claim labeled:\nmeasured / from\ndocumentation /\nretracted",
            "sekcija": "Section at the TOP:\n3 findings retracted,\n3 directionally correct,\nwrong in magnitude",
            "suprotan": "Finding in the opposite\ndirection:\nfix ALREADY\nshipped,\njust a forgotten\nswitch",
            "zvoni": "Alert ringing\nCONTINUOUSLY for ~10\nweeks —\ndeliberately at the top of the list",
            "poredjenje": "Comparison: how many\nrecommendations\nare actually in the\nwork-tracking system?",
            "odgovor": "Answer: almost\nnone —\nfindings existed, but no one\nwas formally responsible",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]

    g = Digraph("ch30_ciklus_revizije", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.5", ranksep="0.7", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    # -- Row 1: five review passes ---------------------------------------
    with g.subgraph(name="row1") as r:
        r.attr(rank="same")
        r.node("p1", n["p1"])
        r.node("p2", n["p2"])
        r.node("p34", n["p34"])
        r.node("p5", n["p5"])
    g.edge("p1", "p2")
    g.edge("p2", "p34")
    g.edge("p34", "p5")

    g.node("oznaka", n["oznaka"], shape="hexagon", fillcolor=BOX_FILL, color=BOX_LINE)
    g.edge("p2", "oznaka")

    g.node("sekcija", n["sekcija"], fillcolor=NOTE_FILL, color=NOTE_LINE)
    g.edge("oznaka", "sekcija")

    with g.subgraph(name="row_red") as r:
        r.attr(rank="same")
        r.node("suprotan", n["suprotan"], fillcolor=RED_FILL, color=RED_LINE)
        r.node("zvoni", n["zvoni"], fillcolor=RED_FILL, color=RED_LINE)
    g.edge("sekcija", "suprotan")
    g.edge("sekcija", "zvoni")

    g.node("poredjenje", n["poredjenje"], shape="hexagon", fillcolor=BOX_FILL, color=BOX_LINE)
    g.edge("suprotan", "poredjenje")
    g.edge("zvoni", "poredjenje")

    g.node("odgovor", n["odgovor"], shape="box", style="rounded,filled",
           fillcolor=NOTE_FILL, color=NOTE_LINE)
    g.edge("poredjenje", "odgovor")

    out_path = OUT_DIR / f"ch30-ciklus-revizije{cfg['suffix']}.png"
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
