#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch01-tri-uzroka.png (sr) / ch01-tri-uzroka.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch01_tri_uzroka.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'TRI NEZAVISNO TAČNA ZAPAŽANJA', 'body': "jedan dashboard pokazuje kvarove  •  nijedan\nalarm nije stigao  •  glavni dashboard prikazuje\nnula kvarova čak i na filteru 'Sve'", 'connector': None}, {'title': 'TRI NEZAVISNA UZROKA, ISTI REZULTAT', 'body': "gejt oblikovan za nalet ne može da se okine na\ncurenje  •  'Sve' na filteru nije zaista sve  •\nposao uopšte nije instrumentisan", 'connector': 'samo jedan raniji signal,\nupisan pre gejta i nezavisno\nod instrumentacije, rekao\nistinu'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'THREE INDEPENDENTLY TRUE OBSERVATIONS', 'body': "one dashboard shows failures  •  no\nalert ever fired  •  the main dashboard shows\nzero failures even on the 'All' filter", 'connector': None}, {'title': 'THREE INDEPENDENT CAUSES, THE SAME RESULT', 'body': "a gate shaped for a burst can't trigger on a\nslow leak  •  'All' on the filter isn't really all  •\nthe job isn't instrumented at all", 'connector': 'only one earlier signal,\nrecorded before the gate and\nindependent of instrumentation,\ntold the truth'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch01-tri-uzroka{cfg['suffix']}.png"
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
