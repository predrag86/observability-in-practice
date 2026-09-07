#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch18-deljeni-kolektor.png (sr) / ch18-deljeni-kolektor.en.png
(en) — the shared-collector funnel diagram for Chapter 18. The sr PNG is
already committed (hand-authored); this script's "sr" path is for
documentation/future regeneration only. Usage: python3 ch18_deljeni_kolektor.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _graphflow import new_figure, box, arrow, save

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": dict(
        a="Provajderov API za metrike\ninstance\nstatički, imenovani poslovi po\ninstanci",
        b="Baza-instanca, pisac\ndirektan TLS na endpoint\ninstance,\nnamenska uloga, ograničen\nbroj konekcija",
        c="Baza-instanca, čitalac\ndirektan TLS na endpoint\ninstance,\nnamenska uloga, ograničen\nbroj konekcija",
        collector="Deljeni kolektor\nisti koji nosi ostatak flote",
        platform="Platforma za posmatranje\njedan identifikator instance;\nuloga iz sopstvenog statusa replikacije",
    ),
    "en": dict(
        a="Provider's metrics API\ninstances\nstatic, named jobs per instance",
        b="Database instance, writer\ndirect TLS to the instance\nendpoint,\ndedicated role, limited\nconnection count",
        c="Database instance, reader\ndirect TLS to the instance\nendpoint,\ndedicated role, limited\nconnection count",
        collector="Shared collector\nthe same one that carries the rest of the fleet",
        platform="Observability platform\none instance identifier;\nrole from its own replication status",
    ),
}


def build(lang):
    t = TEXT[lang]
    fig, ax = new_figure(11.5, 8.2)

    box(ax, 0.3, 5.3, 3.6, 2.0, t["a"], fontsize=10.5)
    box(ax, 4.2, 5.3, 3.2, 2.0, t["b"], fontsize=10)
    box(ax, 7.7, 5.3, 3.2, 2.0, t["c"], fontsize=10)

    box(ax, 3.9, 3.2, 3.8, 1.5, t["collector"], fontsize=11)
    box(ax, 3.9, 0.6, 3.8, 1.9, t["platform"], fontsize=10.5)

    arrow(ax, (2.1, 5.3), (4.9, 4.7), curved=-0.25)
    arrow(ax, (5.8, 5.3), (5.8, 4.7))
    arrow(ax, (9.3, 5.3), (5.7, 4.7), curved=0.25)
    arrow(ax, (5.8, 3.2), (5.8, 2.5))

    suffix = "" if lang == "sr" else ".en"
    save(fig, OUT_DIR / f"ch18-deljeni-kolektor{suffix}.png")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "en"
    for lang in (TEXT if which == "all" else [which]):
        build(lang)


if __name__ == "__main__":
    main()
