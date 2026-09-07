#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch16-pogresno-usmeravanje.png (sr) / ch16-pogresno-usmeravanje.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch16_pogresno_usmeravanje.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'GRUBO GRANANJE (PRE)', 'body': 'svaki pad zadatka bez razlikovanja\ntipa greške vodi u runbook za\nkašnjenje ulaznih podataka', 'connector': None}, {'title': 'REZULTAT', 'body': "otkaz zbog prekida konekcije ka bazi\nusmeren u pogrešan runbook —\nsvih 6 od 6 slučajeva u mesec dana\npogrešno pročitano kao 'kasni izvor'", 'connector': 'nedovoljno fin otisak'}, {'title': 'FINO GRANANJE (POSLE)', 'body': 'usmeravanje po tipu izuzetka iz same\nporuke alarma — otkaz konekcije ide u\nsopstveni, tačan runbook, automatski', 'connector': 'dodat poseban fingerprint'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'COARSE BRANCHING (BEFORE)', 'body': 'every task failure, with no distinction\nby error type, routes into the runbook\nfor late input data', 'connector': None}, {'title': 'RESULT', 'body': "a failure from a dropped database\nconnection routed to the wrong runbook —\nall 6 of 6 cases in a month misread\nas 'late source'", 'connector': 'not a fine-grained enough\nfingerprint'}, {'title': 'FINE-GRAINED BRANCHING (AFTER)', 'body': 'routing by exception type straight from\nthe alert message itself — a connection\nfailure goes to its own, correct runbook,\nautomatically', 'connector': 'a dedicated fingerprint added'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch16-pogresno-usmeravanje{cfg['suffix']}.png"
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
