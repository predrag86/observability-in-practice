#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch14-slack-spof.png (sr) / ch14-slack-spof.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch14_slack_spof.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'PRVI POKUŠAJ (POGREŠAN)', 'body': "email dodat na više obični alarma\n'da ne bi nešto promašili' — svaki\nod njih sad duplira poruku u\nčetiri sandučeta, svaki put", 'connector': None}, {'title': 'USVOJENO REŠENJE', 'body': "email vezan ISKLJUČIVO za alarme\nčije paljenje znači 'sama isporuka\nka Slack-u je pukla' — sanduče ćuti\ndok Slack radi", 'connector': 'ispravljeno isti dan'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'FIRST ATTEMPT (WRONG)', 'body': "email added to several ordinary alerts\n'just in case' — each of them now\nduplicates the message into four\ninboxes, every time", 'connector': None}, {'title': 'ADOPTED SOLUTION', 'body': "email wired ONLY to alerts whose firing\nmeans 'delivery to Slack itself broke' —\nthe inbox stays silent while Slack works", 'connector': 'fixed the same day'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch14-slack-spof{cfg['suffix']}.png"
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
