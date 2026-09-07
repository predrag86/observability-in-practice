#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch26-lanac-ovlascenja.png (sr) / ch26-lanac-ovlascenja.en.png (en) — the stacked-box-flow
diagram for this chapter. The sr PNG here is already committed
(hand-authored); this script's "sr" path exists for documentation/future
regeneration only. Usage: python3 ch26_lanac_ovlascenja.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _boxflow import Box, render_boxflow

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": {"suffix": "", "boxes": [{'title': 'DUGME U CHAT KANALU', 'body': 'vidljivo SAMO članovima kanala —\nplatforma za poruke nema\nodobrenje na nivou dugmeta', 'connector': None}, {'title': 'JAVNI OKIDAČ, PROVEREN POTPISOM', 'body': 'URL mora biti javan (nema potpisivanja\nka oblaku), pa autentičnost dolazi od\nHMAC potpisa poruke + vremenskog\nprozora — bez ključa, zahtev se odbija', 'connector': 'članstvo u kanalu JESTE\nkontrola pristupa'}, {'title': 'NAJUŽA MOGUĆA ULOGA', 'body': 'samo jedna funkcija sme da\npokrene zadatak, uloga ograničena\nna tačno tri dozvoljena cilja', 'connector': 'potpis prolazi'}]},
    "en": {"suffix": ".en", "boxes": [{'title': 'BUTTON IN THE CHAT CHANNEL', 'body': 'visible ONLY to channel members —\nthe messaging platform has no\nbutton-level permission', 'connector': None}, {'title': 'PUBLIC TRIGGER, VERIFIED BY SIGNATURE', 'body': "the URL must be public (no signing\ntoward the cloud), so authenticity comes\nfrom the message's HMAC signature + a\ntime window — without the key, the request is rejected", 'connector': 'channel membership IS\nthe access control'}, {'title': 'THE NARROWEST POSSIBLE ROLE', 'body': 'only one function is allowed to\nlaunch the task, the role is limited\nto exactly three permitted targets', 'connector': 'signature passes'}]},
}


def build(lang):
    cfg = TEXT[lang]
    boxes = [Box(**b) for b in cfg["boxes"]]
    out_path = OUT_DIR / f"ch26-lanac-ovlascenja{cfg['suffix']}.png"
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
