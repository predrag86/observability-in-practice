#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch06-flush-prozor.png (sr) / ch06-flush-prozor.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch06_flush_prozor.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'Hop 1: aplikacija  →  sidecar (localhost)', 'body': 'asinhroni bafer raspona/logova (Batch processor)\n→  NIJE pokriveno stopTimeout-om', 'connector': None}, {'title': 'Hop 2: sidecar  →  gateway', 'body': 'stopTimeout: 30s daje sidecar-u vreme da isprazni\n→  OVO je pokriveno flush prozorom', 'connector': 'zadatak se gasi'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'Hop 1: application  →  sidecar (localhost)', 'body': 'asynchronous span/log buffer (Batch processor)\n→  NOT covered by stopTimeout', 'connector': None}, {'title': 'Hop 2: sidecar  →  gateway', 'body': 'stopTimeout: 30s gives the sidecar time to drain\n→  THIS is covered by the flush window', 'connector': 'the task is shutting down'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch06-flush-prozor{cfg['suffix']}.png"
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
