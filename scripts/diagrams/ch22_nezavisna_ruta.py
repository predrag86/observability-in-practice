#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch22-nezavisna-ruta.png (sr) / ch22-nezavisna-ruta.en.png (en)
— the independent-route diagram for Chapter 22. The sr PNG is already
committed (hand-authored); this script's "sr" path is for
documentation/future regeneration only. Usage: python3 ch22_nezavisna_ruta.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _graphflow import new_figure, box, container, arrow, save

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": dict(
        main_route="Glavna ruta — isti\nkolektor/cevovod koji nosi ostatak telemetrije",
        main_rule="Pravilo za mrežne alarme\nevaluira nad tim istim putem",
        indep_route="Nezavisna ruta — odvojen\nizvor podataka, mimo deljenog kolektora",
        indep_rule="Pravilo za par kritičnih alarma\nevaluira direktno, bez\nte zavisnosti",
        collector="Kolektor/cevovod\npadne",
        lbl_main_quiet="glavna ruta utihne —\nneraspoznatljivo od\n'sve je u redu'",
        lbl_indep_ok="nezavisna ruta\ni dalje radi",
        channel="Isti kanal za obaveštavanje",
    ),
    "en": dict(
        main_route="Main route — the same\ncollector/pipeline that carries\nthe rest of the telemetry",
        main_rule="Rule for network alerts\nevaluates over that same path",
        indep_route="Independent route — a separate\ndata source, bypassing the\nshared collector",
        indep_rule="Rule for a pair of critical alerts\nevaluates directly, without\nthat dependency",
        collector="Collector/pipeline\ngoes down",
        lbl_main_quiet="main route falls quiet —\nindistinguishable from\n'everything is fine'",
        lbl_indep_ok="independent route\nstill works",
        channel="Same notification channel",
    ),
}


def build(lang):
    t = TEXT[lang]
    fig, ax = new_figure(11.8, 10.6)

    container(ax, 0.1, 2.5, 5.0, 5.1)
    container(ax, 6.7, 2.5, 5.0, 5.1)

    box(ax, 0.4, 6.2, 4.4, 1.2, t["main_route"], fontsize=9.6)
    box(ax, 0.55, 2.8, 4.1, 1.5, t["main_rule"], fontsize=10)
    arrow(ax, (2.6, 6.2), (2.6, 4.3))

    box(ax, 7.0, 6.2, 4.4, 1.2, t["indep_route"], fontsize=9.6)
    box(ax, 7.15, 2.8, 4.1, 1.5, t["indep_rule"], fontsize=9.6)
    arrow(ax, (9.2, 6.2), (9.2, 4.3))

    box(ax, 4.55, 8.2, 2.7, 1.2, t["collector"], fontsize=9.6)
    arrow(ax, (4.9, 8.2), (2.8, 4.6), dotted=True, curved=-0.15,
          label=t["lbl_main_quiet"], label_dx=-1.55, label_dy=1.5, fontsize=8.6)
    arrow(ax, (7.0, 8.2), (9.0, 4.6), dotted=True, curved=0.15,
          label=t["lbl_indep_ok"], label_dx=1.55, label_dy=1.5, fontsize=8.6)

    box(ax, 4.15, 0.45, 3.5, 1.15, t["channel"], fontsize=10.5)
    arrow(ax, (2.6, 2.8), (5.3, 1.15), curved=-0.15)
    arrow(ax, (9.2, 2.8), (7.1, 1.15), curved=0.15)

    suffix = "" if lang == "sr" else ".en"
    save(fig, OUT_DIR / f"ch22-nezavisna-ruta{suffix}.png")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "en"
    for lang in (TEXT if which == "all" else [which]):
        build(lang)


if __name__ == "__main__":
    main()
