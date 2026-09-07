#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch02-dokaz-ne-vreme.png (sr) / ch02-dokaz-ne-vreme.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch02_dokaz_ne_vreme.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'KVAR STIŽE ODMAH POSLE OTEL ROLLOUT-A', 'body': 'izgleda kao regresija instrumentacije —\nsidecar izlazi čisto, aplikacija ne', 'connector': None}, {'title': 'TRI NEZAVISNA DOKAZA ISKLJUČUJU OVERLAY', 'body': 'isti kvar postojao tri dana ranije, druge\ngrane na istom image-u prošle, obrazac prati\noblik podataka — ne oblik instrumentacije', 'connector': 'dokaz, ne vremenska bliskost'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'THE FAILURE ARRIVES RIGHT AFTER THE OTEL ROLLOUT', 'body': "looks like an instrumentation regression —\nthe sidecar exits cleanly, the application doesn't", 'connector': None}, {'title': 'THREE INDEPENDENT PROOFS RULE OUT THE OVERLAY', 'body': 'the same failure existed three days earlier, other\nbranches on the same image passed, the pattern\nfollows the shape of the data — not of the instrumentation', 'connector': 'proof, not timing coincidence'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch02-dokaz-ne-vreme{cfg['suffix']}.png"
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
