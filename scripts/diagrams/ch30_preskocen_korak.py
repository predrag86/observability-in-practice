#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch30-preskocen-korak.png (sr) / ch30-preskocen-korak.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch30_preskocen_korak.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'PLANIRAN KORAK PRESKOČEN', 'body': 'drugi sloj plana (bočni kolektor)\nveć rešava isti problem čistije —\nprocenjen najgori gubitak je mali\ni imenovan brojkom, ne pretpostavkom', 'connector': None}, {'title': 'ZAPISAN USLOV ZA POVRATAK', 'body': 'ako pilot otkrije merljiv gubitak\npodataka, preskočeni korak se\nvraća na plan — bez ovog uslova\npreskakanje bi bilo nadanje', 'connector': 'proverljiva opklada, ne nada'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'PLANNED STEP SKIPPED', 'body': 'a second layer of the plan (the\nsidecar collector) already solves the\nsame problem more cleanly — the\nestimated worst case is small and\nnamed as a number, not an assumption', 'connector': None}, {'title': 'A WRITTEN-DOWN CONDITION FOR GOING BACK', 'body': 'if the pilot reveals a measurable\ndata loss, the skipped step goes\nback on the plan — without this\ncondition, skipping would just be hoping', 'connector': 'a verifiable bet, not hope'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch30-preskocen-korak{cfg['suffix']}.png"
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
