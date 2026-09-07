#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch23-zivotni-ciklus.png (sr) / ch23-zivotni-ciklus.en.png (en)
— the task-lifecycle diagram for Chapter 23. The sr PNG is already
committed (hand-authored); this script's "sr" path is for
documentation/future regeneration only. Usage: python3 ch23_zivotni_ciklus.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _graphflow import new_figure, box, arrow, save

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": dict(
        trigger="Okidač → predaja zadatka →\nred čekanja\n(uvek najnovija revizija;\npredat → na čekanju → spreman)",
        capacity="Izbor izvora kapaciteta\nredosled: prvo red 1, red 2\nsamo kao rezerva",
        run="Izvršavanje kao obična\ninstanca kontejnerske infrastrukture\n→ izlazni kod",
        success="Uspeh\n(izlazni kod nula)",
        resubmit="Ponovna predaja\n(prolazan uzrok, do gornje\ngranice pokušaja)",
        permanent="Trajni neuspeh\n(trajan uzrok, ne pokušava\nponovo)",
    ),
    "en": dict(
        trigger="Trigger → task submission →\nqueue\n(always the latest revision;\nsubmitted → waiting → ready)",
        capacity="Choosing a capacity source\norder: queue 1, queue 2\nonly as a fallback",
        run="Runs as an ordinary\ncontainer-infra instance\n→ exit code",
        success="Success\n(exit code zero)",
        resubmit="Resubmitted\n(transient cause, up to a\nretry ceiling)",
        permanent="Permanent failure\n(persistent cause, doesn't\nretry)",
    ),
}


def build(lang):
    t = TEXT[lang]
    fig, ax = new_figure(12.6, 9.6)

    box(ax, 2.0, 7.7, 6.6, 1.75, t["trigger"], fontsize=10.5)

    box(ax, 0.3, 5.5, 4.6, 1.55, t["capacity"], fontsize=10)
    arrow(ax, (3.3, 7.7), (2.6, 7.05), curved=-0.1)

    box(ax, 0.3, 3.1, 4.6, 1.85, t["run"], fontsize=10.5)
    arrow(ax, (2.6, 5.5), (2.6, 4.95))

    box(ax, 0.3, 0.4, 2.4, 1.35, t["success"], fontsize=10)
    box(ax, 3.3, 0.4, 3.3, 1.35, t["resubmit"], fontsize=9.6)
    box(ax, 7.1, 0.4, 3.0, 1.35, t["permanent"], fontsize=9.3)

    arrow(ax, (1.5, 3.1), (1.5, 1.75))
    arrow(ax, (3.4, 3.1), (4.5, 1.75), curved=0.12)
    arrow(ax, (4.85, 3.1), (8.0, 1.75), curved=0.22)

    # retry loop back up to the top box, routed to the right of the "permanent failure" box
    arrow(ax, (6.5, 1.75), (8.5, 7.7), curved=-0.55, lw=1.6)

    suffix = "" if lang == "sr" else ".en"
    save(fig, OUT_DIR / f"ch23-zivotni-ciklus{suffix}.png")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "en"
    for lang in (TEXT if which == "all" else [which]):
        build(lang)


if __name__ == "__main__":
    main()
