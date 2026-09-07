#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch28-lazni-uspeh.png (sr) / ch28-lazni-uspeh.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch28_lazni_uspeh.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'DVA MOGUĆA ISHODA UPISA', 'body': 'token samo-za-čitanje: promena tiho\nblokirana  •  token sa dozvolom pisanja:\npromena zaista sprovedena', 'connector': None}, {'title': "AGENT PRIJAVLJUJE: 'USPEŠNO OBRISANO'", 'body': 'identičan odgovor u oba slučaja —\nagent nema način da iznutra vidi razliku,\npa granica mora biti sprovedena na opsegu tokena', 'connector': 'platforma vraća istu poruku\nbez obzira šta se stvarno\ndesilo'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'TWO POSSIBLE WRITE OUTCOMES', 'body': 'read-only token: the change is silently\nblocked  •  token with write permission:\nthe change is actually carried out', 'connector': None}, {'title': "AGENT REPORTS: 'SUCCESSFULLY DELETED'", 'body': 'identical response in both cases —\nthe agent has no way to see the difference\nfrom inside, so the boundary must be enforced at the token-scope level', 'connector': 'the platform returns the same\nmessage regardless of what\nactually happened'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch28-lazni-uspeh{cfg['suffix']}.png"
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
