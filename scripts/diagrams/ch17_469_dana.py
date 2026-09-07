#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch17-469-dana.png (sr) / ch17-469-dana.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch17_469_dana.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'PRELAZ U ALARM — dan 0', 'body': 'zadatak počinje da otkazuje,\nalarm ispravno prelazi u stanje\nalarmiranja i pošalje TAČNO\njedno obaveštenje', 'connector': None}, {'title': '469 DANA TIŠINE', 'body': 'zadatak nastavlja da otkazuje\nsvaki put — alarm ostaje aktivan,\nali ne šalje NIJEDNO novo\nobaveštenje, jer stanje se\nnikad nije promenilo', 'connector': 'obaveštava se SAMO na\npromenu stanja'}, {'title': 'OTKRIVENO SLUČAJNO', 'body': 'tokom nevezanog čišćenja koda —\nne pretragom, ne dashboard-om,\nslučajnim kontaktom', 'connector': 'niko nije tražio, niko nije video'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'TRANSITION INTO ALERT — day 0', 'body': 'the task starts failing, the alert\ncorrectly transitions into the\nfiring state and sends EXACTLY\none notification', 'connector': None}, {'title': '469 DAYS OF SILENCE', 'body': 'the task keeps failing every\ntime — the alert stays active,\nbut sends NOT ONE new\nnotification, because the state\nnever changed', 'connector': 'notification fires ONLY on\na state change'}, {'title': 'DISCOVERED BY ACCIDENT', 'body': 'during unrelated code cleanup —\nnot by search, not by a dashboard,\nby accidental contact', 'connector': 'nobody looked, nobody saw'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch17-469-dana{cfg['suffix']}.png"
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
