#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch27-tri-sloja" diagram used in
Poglavlje 27 / Chapter 27 (prioritizacija / prioritization).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch27-tri-sloja.png was hand-built with no source file kept alongside it,
so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch27_tri_sloja.py sr   # -> docs/diagrams/ch27-tri-sloja.png
    python3 scripts/diagrams/ch27_tri_sloja.py en   # -> docs/diagrams/ch27-tri-sloja.en.png
    python3 scripts/diagrams/ch27_tri_sloja.py all  # both

Structure note: three layers of the same backlog -- the full backlog
(gray, storage of detail) narrows via a ranking edge into the short
top-N shortlist (tan, the decision view). The shortlist and the
"honorable mention" section (tan, below the promotion threshold) feed
each other: items drop below threshold into honorable mention, and
promotion pulls them back up when the shortlist shrinks. A finished
shortlist item is deleted (dashed, unfilled terminal -- deliberately not
archived/struck-through), and every shortlist change is also logged,
dotted, into a dated changelog record (gray cylinder).
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"
NOTE_FILL = "#F4EFE6"
NOTE_LINE = "#8B7355"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch27-tri-sloja.png (default locale, no suffix)
        "nodes": {
            "backlog": "Pun backlog\n(skladište detalja,\nrunbook-ovi,\nsvi nalazi, sve domene)",
            "shortlist": "Kratak rangiran spisak\n(top 10-15, PO\nDOMENU:\nbezbednost /\nperformanse /\npouzdanost / trošak)",
            "honorable": "Časna pomena\n(svesno rangirano niže,\nsa razlogom)",
            "delete": "OBRIŠI sa spiska\n(ne arhiviraj precrtano)",
            "changelog": "Datiran zapis promena:\nšta dodato/uklonjeno, i\nzašto",
        },
        "edges": {
            "rank": "rangiranje: domet x\nverovatnoća x trošak\npopravke\nspoji nalaze sa istim\nkorenom uzroka",
            "below": "ispod praga, ali\nrazmotreno",
            "promote": "promocija kad se top\nspisak skrati",
            "done": "stavka završena",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch27-tri-sloja.en.png
        "nodes": {
            "backlog": "Full backlog\n(store of detail,\nrunbooks,\nall findings, all domains)",
            "shortlist": "Short ranked list\n(top 10-15, PER\nDOMAIN:\nsecurity /\nperformance /\nreliability / cost)",
            "honorable": "Honorable mention\n(deliberately ranked lower,\nwith a reason)",
            "delete": "DELETE from the list\n(don't archive struck-through)",
            "changelog": "Dated changelog:\nwhat was added/removed, and\nwhy",
        },
        "edges": {
            "rank": "ranking: reach x\nlikelihood x fix\ncost\nmerge findings sharing\nthe same root cause",
            "below": "below threshold, but\nconsidered",
            "promote": "promotion when the top\nlist shrinks",
            "done": "item finished",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    e = cfg["edges"]

    g = Digraph("ch27_tri_sloja", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.6", ranksep="0.7", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("backlog", n["backlog"])
    g.node("shortlist", n["shortlist"], fillcolor=NOTE_FILL, color=NOTE_LINE)
    g.node("honorable", n["honorable"], fillcolor=NOTE_FILL, color=NOTE_LINE)
    g.node("delete", n["delete"], shape="box", style="rounded,dashed",
           fillcolor="white", color=BOX_LINE)
    g.node("changelog", n["changelog"], shape="cylinder",
           fillcolor=BOX_FILL, color=BOX_LINE)

    g.edge("backlog", "shortlist", label=e["rank"])
    g.edge("shortlist", "honorable", label=e["below"])
    g.edge("honorable", "shortlist", label=e["promote"])
    g.edge("shortlist", "delete", label=e["done"], style="dashed")
    g.edge("shortlist", "changelog", style="dotted")

    out_path = OUT_DIR / f"ch27-tri-sloja{cfg['suffix']}.png"
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
