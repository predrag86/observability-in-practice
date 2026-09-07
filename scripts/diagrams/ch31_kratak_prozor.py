#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch31-kratak-prozor.png (sr) / ch31-kratak-prozor.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch31_kratak_prozor.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'SEDMODNEVNI PROZOR', 'body': 'dosledan rast koji liči na\ncurenje — matematički tačan\nizračun na dostupnim podacima', 'connector': None}, {'title': '+4 DANA VIŠE PODATAKA', 'body': 'trend se PREOKREĆE — rast je bio\ndeo šireg oscilatornog obrasca,\nvrednost se vraća na polaznu tačku', 'connector': 'pravac je tačan izračunat,\nali prozor prekratak'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'SEVEN-DAY WINDOW', 'body': 'a consistent rise that looks like\na leak — a mathematically correct\ncalculation on the available data', 'connector': None}, {'title': '+4 MORE DAYS OF DATA', 'body': 'the trend REVERSES — the rise was\npart of a wider oscillating pattern,\nthe value returns to its starting point', 'connector': 'the direction is calculated\ncorrectly, but the window\nis too short'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch31-kratak-prozor{cfg['suffix']}.png"
    render_boxflow(out_path, boxes)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "en"
    if which == "all":
        for lang in TEXT:
            build(lang)
    else:
        build(which)


if __name__ == "__main__":
    main()
