#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch13-zamrznut-gauge.png (sr) / ch13-zamrznut-gauge.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch13_zamrznut_gauge.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'KOLEKTOR ŽIV', 'body': 'vrednost se osvežava na svaki\nciklus (npr. na par sati) —\nstarost vrednosti ostaje ispod\npraga pravila', 'connector': None}, {'title': 'KOLEKTOR UMRE', 'body': 'poslednja vrednost se zamrzava\nzauvek — ali vreme i dalje teče,\npa starost te vrednosti raste\nbez granice', 'connector': 'kolektor prestaje da piše'}, {'title': 'LAŽNI KRITIČNI ALARM', 'body': 'starost pređe prag pravila —\nalarm se pali baš ZATO što je\nmonitoring umro, dok je sistem\nkoji se posmatra potpuno zdrav', 'connector': 'prag za starost pređen'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'COLLECTOR ALIVE', 'body': "the value refreshes every\ncycle (e.g. every couple of hours) —\nthe value's age stays below\nthe rule's threshold", 'connector': None}, {'title': 'COLLECTOR DIES', 'body': "the last value freezes forever —\nbut time keeps passing, so\nthat value's age grows\nwithout bound", 'connector': 'the collector stops writing'}, {'title': 'FALSE CRITICAL ALERT', 'body': "the age crosses the rule's threshold —\nthe alert fires precisely BECAUSE the\nmonitoring died, while the system\nbeing observed is completely healthy", 'connector': 'the age threshold is crossed'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch13-zamrznut-gauge{cfg['suffix']}.png"
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
