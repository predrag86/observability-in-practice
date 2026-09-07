#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch08-tiha-praznina.png (sr) / ch08-tiha-praznina.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch08_tiha_praznina.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'STANDARDNA PROVERA', 'body': 'build prolazi · testovi zeleni\nHTTP 200 · aplikacija se učitava\ni radi identično za korisnika', 'connector': None}, {'title': 'ISPORUČENI PAKET', 'body': 'sadrži kod izgrađen iz stare\nverzije izvora — inicijalizacija\nSDK-a jednostavno nije u njemu', 'connector': 'nijedna od ovih provera\nne gleda telemetrijski kod'}, {'title': 'EKSPLICITNA PROVERA', 'body': 'da li isporučeni JS paket sadrži\npoziv inicijalizacije SDK-a?\nda li se naziv servisa uopšte\npojavljuje nizvodno u telemetriji?', 'connector': 'jedini način da se otkrije'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'STANDARD CHECK', 'body': 'build passes · tests green\nHTTP 200 · the app loads and\nworks identically for the user', 'connector': None}, {'title': 'SHIPPED BUNDLE', 'body': "contains code built from an old\nversion of the source — the SDK\ninitialization simply isn't in it", 'connector': 'none of these checks\nlook at the telemetry code'}, {'title': 'EXPLICIT CHECK', 'body': 'does the shipped JS bundle contain\nthe SDK initialization call?\ndoes the service name even\nshow up downstream in telemetry?', 'connector': 'the only way to catch it'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch08-tiha-praznina{cfg['suffix']}.png"
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
