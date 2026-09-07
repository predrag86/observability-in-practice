#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch03-alarm-pre-racuna.png (sr) / ch03-alarm-pre-racuna.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch03_alarm_pre_racuna.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'BUDŽETSKI ALARM NA 95%, RANO UPOZORENJE', 'body': 'anomaly-detektor uočava neobičan rast\npre praga; prekoračenje se NAPLAĆUJE,\nne blokira upis', 'connector': None}, {'title': 'DIJAGNOSTIČKO GRANANJE', 'body': 'kardinalnost metrika ili obim logova?\nsvaki krak vodi ka drugoj,\nkonkretnoj popravci', 'connector': 'isti alarm, dva moguća uzroka'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'BUDGET ALERT AT 95%, AN EARLY WARNING', 'body': "the anomaly detector notices an unusual rise\nbefore the threshold; going over is BILLED,\nit doesn't block the write", 'connector': None}, {'title': 'DIAGNOSTIC BRANCHING', 'body': 'metric cardinality or log volume?\neach branch leads to a different,\nconcrete fix', 'connector': 'same alert, two possible causes'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch03-alarm-pre-racuna{cfg['suffix']}.png"
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
