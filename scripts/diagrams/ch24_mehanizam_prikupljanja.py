#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renders ch24-mehanizam-prikupljanja.png (sr) /
ch24-mehanizam-prikupljanja.en.png (en) — the collection-mechanism diagram
for Chapter 24. The sr PNG is already committed (hand-authored); this
script's "sr" path is for documentation/future regeneration only.
Usage: python3 ch24_mehanizam_prikupljanja.py en
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _graphflow import new_figure, box, container, cylinder, arrow, save

OUT_DIR = Path(__file__).parent.parent.parent / "docs" / "diagrams"

TEXT = {
    "sr": dict(
        platform="Platforma za posmatranje",
        logstore="Skladište logova",
        dashboard="Dashboard najsporijih\nupita",
        alerts="Pravila alarma",
        channel="Kanal za obaveštenja",
        sched_collect="Zakazano prikupljanje",
        sched_rule="Zakazano pravilo\nsvaka tri sata",
        creds="Skladište kredencijala\npar ključeva,\nne lozinka",
        exec_box="Kratkotrajno izvršavanje\n~10-60s, sve tri faze",
        bookmark="Beleška o mestu gde je\nstalo (trajno sačuvan\nvodeni žig)",
        ext_service="Spoljni servis za\nanalitičko skladištenje podataka",
        workload="Stvarno radno opterećenje\n(npr. noćni posao obrade podataka)",
        usage_hist="Ugrađena istorija upotrebe koju\nservis sam vodi, kasni ~40ak\nminuta do nekoliko sati",
        compute="Namenska radna jedinica,\nnajmanje veličine, minimalno\nvreme naplate po buđenju",
        lbl_1="1 pokreće",
        lbl_creds="kredencijali",
        lbl_2="2 čita\nbelešku",
        lbl_6="6 pomera\nbelešku",
        lbl_query_finish="upit se završi",
        lbl_reads="čita",
        lbl_4="4 redovi, najstariji prvo,\nsa gornjom granicom",
        lbl_3="3 upit kao namenski identitet,\nsamo redovi posle beleške",
        lbl_5="5 sanitizovani zapisi",
    ),
    "en": dict(
        platform="Observability platform",
        logstore="Log store",
        dashboard="Slowest-queries\ndashboard",
        alerts="Alert rules",
        channel="Notification channel",
        sched_collect="Scheduled collection",
        sched_rule="Scheduled rule\nevery three hours",
        creds="Credential store\na couple of keys,\nnot a password",
        exec_box="Short-lived execution\n~10-60s, all three phases",
        bookmark="Bookmark of where it\nleft off (durable,\nwatermarked)",
        ext_service="External service for\nanalytical data storage",
        workload="Actual workload\n(e.g. a nightly data-processing job)",
        usage_hist="Built-in usage history the service\nkeeps itself, lags ~40 min\nto a few hours",
        compute="Dedicated compute unit,\nsmallest size, minimum billed\ntime per wake",
        lbl_1="1 triggers",
        lbl_creds="credentials",
        lbl_2="2 reads the\nbookmark",
        lbl_6="6 moves the\nbookmark",
        lbl_query_finish="query finishes",
        lbl_reads="reads",
        lbl_4="4 rows, oldest first,\nwith an upper bound",
        lbl_3="3 query as a dedicated identity,\nonly rows after the bookmark",
        lbl_5="5 sanitized records",
    ),
}


def build(lang):
    t = TEXT[lang]
    fig, ax = new_figure(16.5, 11.2)

    # Left container: platform / logs / alerting
    container(ax, 0.2, 0.2, 3.9, 8.0)
    box(ax, 0.5, 6.9, 3.3, 1.0, t["platform"], fontsize=10)
    cylinder(ax, 1.35, 5.15, 1.6, 1.35, t["logstore"], fontsize=9.5)
    arrow(ax, (2.15, 6.9), (2.15, 6.5))

    box(ax, 0.45, 3.05, 1.75, 1.35, t["dashboard"], fontsize=9)
    box(ax, 2.35, 3.05, 1.6, 1.35, t["alerts"], fontsize=9.5)
    arrow(ax, (1.7, 5.15), (1.35, 4.4), curved=-0.1)
    arrow(ax, (2.6, 5.15), (3.05, 4.4), curved=0.1)

    box(ax, 1.1, 0.5, 2.3, 1.35, t["channel"], fontsize=9.5)
    arrow(ax, (3.15, 3.05), (2.4, 1.85), curved=0.1)

    # Middle container: scheduled short-lived execution
    container(ax, 4.5, 0.2, 6.2, 10.6)
    box(ax, 4.85, 9.15, 3.0, 1.1, t["sched_collect"], fontsize=10)
    box(ax, 4.85, 7.35, 3.0, 1.1, t["sched_rule"], fontsize=9.5)
    arrow(ax, (6.35, 9.15), (6.35, 8.45))

    cylinder(ax, 8.3, 7.55, 1.9, 1.55, t["creds"], fontsize=8.3)

    box(ax, 5.6, 4.85, 3.9, 1.75, t["exec_box"], fontsize=10)
    arrow(ax, (6.35, 7.35), (6.9, 6.6), curved=-0.1, label=t["lbl_1"], label_dx=-0.75, label_dy=0.15, fontsize=8.6)
    arrow(ax, (8.9, 7.55), (8.3, 6.6), curved=0.1, label=t["lbl_creds"], label_dx=0.75, label_dy=0.15, fontsize=8.6)

    cylinder(ax, 6.2, 2.35, 2.3, 1.55, t["bookmark"], fontsize=8.0)
    arrow(ax, (6.9, 3.9), (6.9, 4.85), label=t["lbl_2"], label_dx=-1.15, label_dy=0.0, fontsize=8.3)
    arrow(ax, (7.9, 4.85), (7.9, 3.9), label=t["lbl_6"], label_dx=0.55, label_dy=-0.35, fontsize=8.3)

    # Right container: external service
    container(ax, 11.0, 3.1, 5.2, 7.7)
    box(ax, 11.35, 9.35, 4.5, 1.1, t["ext_service"], fontsize=9.5)
    box(ax, 11.35, 7.45, 4.5, 1.1, t["workload"], fontsize=8.8)
    arrow(ax, (13.6, 9.35), (13.6, 8.55))

    cylinder(ax, 11.55, 5.35, 4.0, 1.6, t["usage_hist"], fontsize=8.2)
    arrow(ax, (13.6, 7.45), (13.6, 6.95), label=t["lbl_query_finish"], label_dx=1.35, label_dy=0.0, fontsize=8.3)

    box(ax, 11.55, 3.35, 4.0, 1.55, t["compute"], fontsize=8.6)
    arrow(ax, (13.0, 5.35), (13.0, 4.9), label=t["lbl_reads"], label_dx=0.65, label_dy=0.0, fontsize=8.3)

    # cross-container arrows
    arrow(ax, (11.5, 6.1), (9.55, 5.75), curved=0.15, label=t["lbl_4"], label_dx=0.0, label_dy=0.55, fontsize=8.3)
    arrow(ax, (9.5, 5.5), (11.5, 4.1), curved=-0.15, label=t["lbl_3"], label_dx=-0.1, label_dy=-1.0, fontsize=8.3)
    arrow(ax, (5.6, 5.2), (2.5, 4.0), curved=0.15, label=t["lbl_5"], label_dx=-0.3, label_dy=0.9, fontsize=8.6)

    suffix = "" if lang == "sr" else ".en"
    save(fig, OUT_DIR / f"ch24-mehanizam-prikupljanja{suffix}.png")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "en"
    for lang in (TEXT if which == "all" else [which]):
        build(lang)


if __name__ == "__main__":
    main()
