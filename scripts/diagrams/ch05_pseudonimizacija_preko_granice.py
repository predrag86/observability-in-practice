#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch05-pseudonimizacija-preko-granice.png (sr) / ch05-pseudonimizacija-preko-granice.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch05_pseudonimizacija_preko_granice.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'STANJE (izmereno)', 'body': 'Browser: pseudonimni ID  ·  Backend: STVARNI email\n→  spojen trag preko trace propagacije de-anonimizovan', 'connector': None}, {'title': 'IDENTIFIKOVANA POPRAVKA (nije sprovedena)', 'body': 'Backend: keyed-HMAC pseudonim istog korisnika\n→  spojen trag ostaje pseudoniman od kraja do kraja', 'connector': 'popravka: pseudonimizuj i na\nbackend strani'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'STATE (measured)', 'body': 'Browser: pseudonymous ID  ·  Backend: REAL email\n→  the joined trace, via trace propagation, is de-anonymized', 'connector': None}, {'title': 'IDENTIFIED FIX (not implemented)', 'body': 'Backend: keyed-HMAC pseudonym of the same user\n→  the joined trace stays pseudonymous end to end', 'connector': 'fix: pseudonymize on the\nbackend side too'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch05-pseudonimizacija-preko-granice{cfg['suffix']}.png"
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
