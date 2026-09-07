#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch21-redosled-vracanja.png (sr) / ch21-redosled-vracanja.en.png
(en) — the restoration-order diagram for Chapter 21. The sr PNG is already
committed (hand-authored); this script's "sr" path is for
documentation/future regeneration only. Usage: python3 ch21_redosled_vracanja.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _graphflow import new_figure, box, container, arrow, save

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": dict(
        obvious="'Očigledan' redosled:\nprvo dodaj pravilo koje čita\noznaku",
        broken="Ne radi — oznaka je i dalje\nagregirana, upit tiho\nvraća prazno",
        correct="Ispravan redosled:\nprvo ukloni agregaciju\nza tu oznaku",
        confirm="Potvrdi da se oznaka\nzaista vratila",
        permanent="Tek sad dodaj trajno\npravilo koje je drži otvorenom",
    ),
    "en": dict(
        obvious="'Obvious' order:\nfirst add the rule that reads\nthe tag",
        broken="Doesn't work — the tag is still\naggregated, the query silently\nreturns empty",
        correct="Correct order:\nfirst remove the aggregation\nfor that tag",
        confirm="Confirm the tag\nactually came back",
        permanent="Only now add the permanent\nrule that keeps it open",
    ),
}


def build(lang):
    t = TEXT[lang]
    fig, ax = new_figure(9.8, 10.3)

    box(ax, 0.4, 8.3, 4.1, 1.6, t["obvious"], fontsize=10.5)
    box(ax, 5.2, 8.3, 4.2, 1.6, t["broken"], fontsize=10.5)
    arrow(ax, (4.5, 9.1), (5.2, 9.1))

    arrow(ax, (4.6, 8.3), (4.6, 7.4))

    container(ax, 2.3, 0.3, 5.2, 7.0)
    box(ax, 2.7, 5.5, 4.4, 1.5, t["correct"], fontsize=10.5)
    box(ax, 3.0, 3.35, 3.8, 1.35, t["confirm"], fontsize=10.5)
    box(ax, 2.7, 0.7, 4.4, 1.5, t["permanent"], fontsize=10.5)
    arrow(ax, (4.9, 5.5), (4.9, 4.7))
    arrow(ax, (4.9, 3.35), (4.9, 2.2))

    suffix = "" if lang == "sr" else ".en"
    save(fig, OUT_DIR / f"ch21-redosled-vracanja{suffix}.png")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "en"
    for lang in (TEXT if which == "all" else [which]):
        build(lang)


if __name__ == "__main__":
    main()
