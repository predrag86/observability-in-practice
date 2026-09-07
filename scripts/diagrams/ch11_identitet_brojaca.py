#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch11-identitet-brojaca.png (sr) / ch11-identitet-brojaca.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch11_identitet_brojaca.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'IDENTITET INSTANCE OBRISAN', 'body': 'radi uštede na kardinalnosti —\nsve replike pišu u JEDNU kumulativnu seriju', 'connector': None}, {'title': 'STOPA POGREŠNO IZRAČUNATA', 'body': 'pad brojača protumačen kao restart,\nekstrapolisan na vrednost reda veličine\nhiljadu puta veću od stvarne', 'connector': 'ušteda serija, netačna stopa'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'INSTANCE IDENTITY STRIPPED', 'body': 'to save on cardinality —\nall replicas write into ONE cumulative series', 'connector': None}, {'title': 'RATE MISCALCULATED', 'body': 'the counter drop is read as a restart,\nextrapolated to a value roughly a thousand\ntimes larger than the real one', 'connector': 'series saved, rate wrong'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch11-identitet-brojaca{cfg['suffix']}.png"
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
