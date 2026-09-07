#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch19-dve-faze.png (sr) / ch19-dve-faze.en.png (en) — the
two-phase rollout diagram for Chapter 19. The sr PNG is already committed
(hand-authored); this script's "sr" path is for documentation/future
regeneration only. Usage: python3 ch19_dve_faze.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _graphflow import new_figure, box, container, arrow, save

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": dict(
        p1a="Faza 1 — host + log\nsva tri čvora odjednom\nnula rizika, bez restarta",
        p1b="Potvrda end-to-end\npre nastavka na Fazu 2",
        p2a="Faza 2 — izvršni čvorovi,\nredom\nprovera: nema aktivnih\nzadataka\npa restart",
        p2b="Faza 2 — koordinacioni čvor\nnajavljen prozor održavanja",
    ),
    "en": dict(
        p1a="Phase 1 — host + log\nall three nodes at once\nzero risk, no restart",
        p1b="End-to-end confirmation\nbefore continuing to Phase 2",
        p2a="Phase 2 — executor nodes,\nin order\ncheck: no active\ntasks\nthen restart",
        p2b="Phase 2 — coordinator node\nannounced maintenance window",
    ),
}


def build(lang):
    t = TEXT[lang]
    fig, ax = new_figure(10.5, 7.0)

    container(ax, 0.5, 4.3, 9.5, 2.3)
    box(ax, 0.9, 4.6, 3.6, 1.7, t["p1a"], fontsize=10.5)
    box(ax, 5.4, 4.85, 4.2, 1.2, t["p1b"], fontsize=10.5)
    arrow(ax, (4.5, 5.45), (5.4, 5.45))

    arrow(ax, (5.25, 4.3), (5.25, 3.15))

    container(ax, 0.1, 0.3, 9.9, 2.75)
    box(ax, 0.55, 0.55, 3.9, 2.25, t["p2a"], fontsize=10)
    box(ax, 5.4, 0.95, 4.2, 1.45, t["p2b"], fontsize=10)
    arrow(ax, (4.45, 1.65), (5.4, 1.65))

    suffix = "" if lang == "sr" else ".en"
    save(fig, OUT_DIR / f"ch19-dve-faze{suffix}.png")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "en"
    for lang in (TEXT if which == "all" else [which]):
        build(lang)


if __name__ == "__main__":
    main()
