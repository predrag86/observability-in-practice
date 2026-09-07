#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch27-domet-stete.png (sr) / ch27-domet-stete.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch27_domet_stete.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'PRETPOSTAVLJEN DOMET', 'body': "baza za autentikaciju bez replike\nu drugoj zoni — zvuči kao\n'auth ide dole', osrednji rang", 'connector': None}, {'title': 'IZMEREN DOMET', 'body': 'popis stvarnih zavisnosti pokazuje:\nSVAKI API poziv prolazi kroz proveru\nprotiv te baze, ne samo prijava', 'connector': 'neko stvarno popiše\nzavisnosti'}, {'title': 'PONOVO RANGIRANO', 'body': 'isti nalaz, ista jeftina popravka —\nali sad je jasno da je oduvek bio\nrizik za ceo proizvod, ne za deo', 'connector': 'domet, ne problem, se\npromenio'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'ASSUMED BLAST RADIUS', 'body': "an auth database with no replica\nin another zone — sounds like\n'auth goes down', a middling rank", 'connector': None}, {'title': 'MEASURED BLAST RADIUS', 'body': 'the actual dependency inventory shows:\nEVERY API call passes through a check\nagainst that database, not just login', 'connector': 'someone actually inventories\nthe dependencies'}, {'title': 'RE-RANKED', 'body': "same finding, same cheap fix —\nbut now it's clear it was always a\nrisk to the whole product, not a part", 'connector': 'the radius changed,\nnot the problem'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch27-domet-stete{cfg['suffix']}.png"
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
