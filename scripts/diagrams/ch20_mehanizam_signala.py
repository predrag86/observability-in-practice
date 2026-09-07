#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch20-mehanizam-signala.png (sr) / ch20-mehanizam-signala.en.png
(en) — the signal-mechanism diagram for Chapter 20. The sr PNG is already
committed (hand-authored); this script's "sr" path is for
documentation/future regeneration only. Usage: python3 ch20_mehanizam_signala.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _graphflow import new_figure, box, container, arrow, save

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": dict(
        system="Sistem za autentikaciju\ntrejsovi + logovi: guranje, izvorno\nmetrike: samo lokalno izlaganje (povlačenje)",
        unit="Jedna infrastrukturna jedinica\n(dve identične replike u produkciji)",
        sidecar="Prateći kontejner\npovlači metrike na svakih\n~30s\n+ prepisuje identitet izvora po jedinici",
        collector="Kolektor posmatranja",
        platform="Platforma za posmatranje\n(metrike / trejsovi / logovi)",
        lbl_metrics_src="lokalni izvor\nmetrika",
        lbl_traces="trejsovi (uzorak ~par%,\nne podrazumevanih 100%)",
        lbl_logs="logovi",
        lbl_push="metrike, guranje",
    ),
    "en": dict(
        system="Authentication system\ntraces + logs: pushed, at source\nmetrics: local exposure only (pull)",
        unit="A single infrastructure unit\n(two identical replicas in production)",
        sidecar="Sidecar container\npulls metrics every\n~30s\n+ rewrites source identity per unit",
        collector="Observability collector",
        platform="Observability platform\n(metrics / traces / logs)",
        lbl_metrics_src="local metrics\nsource",
        lbl_traces="traces (sampled ~a few%,\nnot the default 100%)",
        lbl_logs="logs",
        lbl_push="metrics, push",
    ),
}


def build(lang):
    t = TEXT[lang]
    fig, ax = new_figure(11.5, 11.0)

    container(ax, 0.3, 4.9, 10.9, 5.8)

    box(ax, 3.9, 8.9, 4.4, 1.6, t["system"], fontsize=10)
    box(ax, 0.7, 5.4, 4.6, 1.7, t["unit"], fontsize=10.5)
    box(ax, 7.9, 6.1, 2.9, 2.1, t["sidecar"], fontsize=9.6)

    box(ax, 4.55, 2.85, 2.9, 1.15, t["collector"], fontsize=11)
    box(ax, 4.1, 0.4, 3.8, 1.35, t["platform"], fontsize=10.5)

    arrow(ax, (8.3, 8.9), (8.9, 8.2), curved=0.15, label=t["lbl_metrics_src"], label_dx=0.9, label_dy=0.1)
    arrow(ax, (4.6, 8.9), (5.2, 4.0), curved=0.2, label=t["lbl_traces"], label_dx=-1.55, label_dy=1.9)
    arrow(ax, (6.1, 8.9), (6.1, 4.0), label=t["lbl_logs"], label_dx=0.55, label_dy=2.0)
    arrow(ax, (8.5, 6.1), (6.3, 3.55), curved=0.2, label=t["lbl_push"], label_dx=1.1, label_dy=-0.05)
    arrow(ax, (6.0, 2.85), (6.0, 1.75))

    suffix = "" if lang == "sr" else ".en"
    save(fig, OUT_DIR / f"ch20-mehanizam-signala{suffix}.png")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "en"
    for lang in (TEXT if which == "all" else [which]):
        build(lang)


if __name__ == "__main__":
    main()
