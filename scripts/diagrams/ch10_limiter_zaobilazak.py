#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch10-limiter-zaobilazak.png (sr) / ch10-limiter-zaobilazak.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch10_limiter_zaobilazak.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'MEMORY_LIMITER JE PRVA STANICA', 'body': 'za sav uobičajen saobraćaj — backpressure\nstiže pre nego što nizvodno išta\npotroši memoriju', 'connector': None}, {'title': 'DVA IZVORA ULAZE MIMO NJE', 'body': 'direktno na batch stanici; OOM sa\nbrojačem odbijanja na nuli je znak\npotrošnje mimo njenog knjigovodstva', 'connector': 'isti pad, dva različita\ndijagnostička obrasca'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'MEMORY_LIMITER IS THE FIRST STATION', 'body': 'for all normal traffic — backpressure\narrives before anything downstream\nspends memory', 'connector': None}, {'title': 'TWO SOURCES ENTER AROUND IT', 'body': 'directly at the batch stage; an OOM\nwith the refused-count counter at zero\nis the sign of consumption outside its bookkeeping', 'connector': 'same crash, two different\ndiagnostic patterns'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch10-limiter-zaobilazak{cfg['suffix']}.png"
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
