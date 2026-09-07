#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch07-prozor-kasnjenje.png (sr) / ch07-prozor-kasnjenje.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch07_prozor_kasnjenje.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'Uzan prozor upita (podrazumevana granularnost)', 'body': "izvor objavljuje tačku sa kašnjenjem  →\nprozor katkad prođe pre nego što tačka postoji  →\npovlačilac čita 'nema tačke' kao 'serija ne postoji'", 'connector': None}, {'title': 'Prošireni prozor upita', 'body': 'dovoljno širok da uhvati i kasno objavljenu tačku  →\nserija ostaje kompletna na svim replikama,\nbez ijedne izmene na strani izvora', 'connector': 'popravka: proširi prozor upita\npreko podrazumevane\ngranularnosti'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'Narrow query window (default granularity)', 'body': "the source publishes the point late  →\nthe window sometimes passes before the point exists  →\nthe puller reads 'no point' as 'series doesn't exist'", 'connector': None}, {'title': 'Widened query window', 'body': 'wide enough to also catch the late-published point  →\nthe series stays complete across all replicas,\nwith no change on the source side', 'connector': 'fix: widen the query window\npast the default granularity'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch07-prozor-kasnjenje{cfg['suffix']}.png"
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
