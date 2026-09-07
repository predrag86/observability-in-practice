#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch25-rotacija-kljuca.png (sr) / ch25-rotacija-kljuca.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch25_rotacija_kljuca.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'ROTACIJA KLJUČA (uobičajena higijena)', 'body': 'menja SVAKI pseudonim odjednom —\nkida longitudinalnu analizu, a ključ\nionako ne štiti sadržaj, samo vezu\npseudonim ↔ email', 'connector': None}, {'title': 'STABILAN KLJUČ (usvojena odluka)', 'body': 'ako je mapiona tabela već\nkompromitovana, rotacija ne pomaže;\nako nije, stabilan ključ ne otvara\nnovi rizik koji bi rotacija zatvorila', 'connector': "ista 'higijena' ovde nosi\ntrošak bez odgovarajuće\ndobiti"}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'KEY ROTATION (standard hygiene)', 'body': "changes EVERY pseudonym at once —\nbreaks longitudinal analysis, and the key\ndoesn't protect content anyway, only the\npseudonym ↔ email link", 'connector': None}, {'title': 'STABLE KEY (adopted decision)', 'body': "if the mapping table is already\ncompromised, rotation doesn't help;\nif it isn't, a stable key doesn't open a\nnew risk that rotation would have closed", 'connector': "the same 'hygiene' here carries\na cost with no matching\nbenefit"}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch25-rotacija-kljuca{cfg['suffix']}.png"
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
