#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch15-dva-ugla.png (sr) / ch15-dva-ugla.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch15_dva_ugla.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'STARI ALARM — RAVAN PRAG', 'body': 'da li je 5xx stopa OVOG TRENUTKA\niznad fiksne granice — trenutan\nsimptom, bez pamćenja istorije', 'connector': None}, {'title': 'NOVI ALARM — BUDŽET GREŠAKA', 'body': 'da li se budžet troši opasnom\nbrzinom, preko dugog i kratkog\nprozora zajedno', 'connector': 'namerno se preklapaju na\nnajbržem nivou —\ndva ugla na isti problem, ne\nduplikat'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'OLD ALERT — FLAT THRESHOLD', 'body': 'is the 5xx rate RIGHT NOW\nabove a fixed line — an instantaneous\nsymptom, with no memory of history', 'connector': None}, {'title': 'NEW ALERT — ERROR BUDGET', 'body': 'is the budget burning at a\ndangerous rate, via a long and a\nshort window together', 'connector': 'they deliberately overlap at\nthe fastest tier —\ntwo angles on the same problem,\nnot a duplicate'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch15-dva-ugla{cfg['suffix']}.png"
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
