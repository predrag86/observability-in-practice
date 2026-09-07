#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch09-slojevi-otkaza.png (sr) / ch09-slojevi-otkaza.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch09_slojevi_otkaza.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'PLITKA PROBA', 'body': 'testira samo da li šelj aplikacije\nuopšte odgovara — može da prođe\ni kad je pozadinski deo sistema\npotpuno nezdrav', 'connector': None}, {'title': 'DUBOKA PROBA', 'body': 'šalje stvaran, ograničen upit ka\nbazi podataka iz aplikacije —\npada tačno kad plitka i dalje\nprolazi', 'connector': 'plitka prolazi, duboka pada  →\nbaza je problem, ne aplikacija'}, {'title': 'PROBA SA RENDEROVANJEM', 'body': 'pokreće pravi browser i proverava\nšta se stvarno prikaže — pada i kad\nobe prethodne prođu, jer kvar je\nisključivo na strani klijenta', 'connector': 'obe prolaze, renderovanje\npada  →  kvar je isključivo\nkod klijenta'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'SHALLOW PROBE', 'body': 'tests only whether the app shell\nresponds at all — it can pass even\nwhen the backend is completely\nunhealthy', 'connector': None}, {'title': 'DEEP PROBE', 'body': 'sends a real, bounded query to the\ndatabase from the application —\nfails exactly when the shallow\nprobe still passes', 'connector': 'shallow passes, deep fails  →\nthe database is the problem,\nnot the application'}, {'title': 'RENDERING PROBE', 'body': 'runs a real browser and checks\nwhat actually renders — fails even\nwhen both earlier probes pass,\nbecause the failure is client-side only', 'connector': 'both pass, rendering fails  →\nthe failure is client-side\nonly'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch09-slojevi-otkaza{cfg['suffix']}.png"
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
