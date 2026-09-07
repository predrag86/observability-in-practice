#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch12-prag-troska.png (sr) / ch12-prag-troska.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch12_prag_troska.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'ISPOD PRAGA ZAPREMINE', 'body': 'upis i zadržavanje padaju na nulu —\nsve što se zadrži stane u uključenu kvotu', 'connector': None}, {'title': 'OBRADA SIROVOG ULAZA OSTAJE', 'body': 'naplaćuje se pre odluke o zadržavanju,\nnezavisno od procenta sampling-a', 'connector': 'sampling štiti dve od tri\nkomponente cene'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'BELOW THE VOLUME THRESHOLD', 'body': 'ingest and retention drop to zero —\neverything retained fits inside the included quota', 'connector': None}, {'title': 'RAW-INGEST PROCESSING STAYS', 'body': "it's billed before the retention decision,\nregardless of the sampling percentage", 'connector': 'sampling protects two of\nthe three cost components'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch12-prag-troska{cfg['suffix']}.png"
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
