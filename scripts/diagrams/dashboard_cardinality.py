#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-cardinality" chart used in
Poglavlje 11 / Chapter 11 (kardinalnost-cena / cardinality-and-cost).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-cardinality.png was hand-built with no source file, so it could
not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_cardinality.py sr   # -> docs/diagrams/dashboard-cardinality.png
    python3 scripts/diagrams/dashboard_cardinality.py en   # -> docs/diagrams/dashboard-cardinality.en.png
    python3 scripts/diagrams/dashboard_cardinality.py all  # both

Data note: illustrative daily active-time-series count over 21 days
(day 0-20), log scale. A quiet baseline around 27k-33k holds through day
5 (Friday evening, when a new histogram with a client-ID label ships),
then the series count explodes to a ~4.3M peak by day 7-8 (discovered
the following Monday), and declines through four remediation phases
back down near the original baseline by day 16-20 -- the shape the
surrounding chapter text describes and the numbers the "16" chapter
refers to when it compares before/after active-series counts.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

DAYS = list(range(0, 21))
SERIES_COUNT = [
    27000, 26000, 27500, 29000, 30000, 32000,      # 0-5: quiet baseline
    620000, 4150000, 4300000,                       # 6-8: Friday-night spike, Monday discovery
    2300000, 2300000,                                # 9-10
    830000, 800000,                                  # 11-12
    360000, 360000,                                  # 13-14
    62000,                                            # 15: remediation phases begin biting
    33000, 32000, 33000, 35000, 37000,               # 16-20: back near baseline
]

CONTRACTED_LIMIT = 10000
FRIDAY_SPIKE_DAY = 5
MONDAY_DISCOVERY_DAY = 8
REMEDIATION_DAY = 15

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-cardinality.png (default locale, no suffix)
        "title": "Aktivan broj vremenskih serija — nalog, 21 dan",
        "xlabel": "dan",
        "ylabel": "aktivne serije (log skala)",
        "limit_label": "ugovoreni limit (10.000)",
        "friday_label": "petak uveče: novi histogram\n+ ID klijenta kao labela",
        "monday_label": "ponedeljak: platforma\njavlja probijen limit",
        "remediation_label": "4 faze sanacije\n(F1→F4)",
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-cardinality.en.png
        "title": "Active time series count — account, 21 days",
        "xlabel": "day",
        "ylabel": "active series (log scale)",
        "limit_label": "contracted limit (10,000)",
        "friday_label": "Friday evening: new histogram\n+ client ID as a label",
        "monday_label": "Monday: platform\nreports limit exceeded",
        "remediation_label": "4 remediation phases\n(F1→F4)",
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
BLUE = "#2A78D6"
ORANGE = "#EB6834"
RED = "#E34948"
GREEN = "#1BAF7A"
GRAY = "#6C6C6C"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(12.4, 4.9), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    ax.plot(
        DAYS, SERIES_COUNT, color=BLUE, linewidth=2.6,
        marker="o", markersize=7.5, markerfacecolor=BLUE,
        markeredgecolor=BLUE, zorder=3,
    )

    ax.set_yscale("log")
    ax.set_xlim(-0.4, 20.4)
    ax.set_ylim(8000, 15000000)

    ax.xaxis.set_major_locator(FixedLocator([0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_major_locator(FixedLocator([1e4, 1e5, 1e6]))
    ax.yaxis.set_minor_locator(NullLocator())

    ax.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    ax.set_axisbelow(True)

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(1.0)

    ax.tick_params(axis="both", labelsize=13, colors=INK, length=0)

    ax.set_xlabel(cfg["xlabel"], fontsize=14.5, color=INK, labelpad=12)
    ax.set_ylabel(cfg["ylabel"], fontsize=14.5, color=INK, labelpad=12)

    ax.set_title(cfg["title"], fontsize=18, fontweight="bold", color=INK, loc="left", pad=16)

    # Contracted-limit reference line.
    ax.axhline(CONTRACTED_LIMIT, color=GRAY, linestyle=(0, (4, 3)), linewidth=1.4, zorder=2)
    ax.text(
        0, CONTRACTED_LIMIT * 1.18, cfg["limit_label"],
        fontsize=13, style="italic", color=GRAY, ha="left", va="bottom",
    )

    # Friday-evening spike start.
    ax.annotate(
        cfg["friday_label"],
        xy=(FRIDAY_SPIKE_DAY, SERIES_COUNT[FRIDAY_SPIKE_DAY] * 1.1),
        xytext=(0.15, 1_250_000),
        fontsize=13, style="italic", color=ORANGE, ha="left", va="bottom",
        arrowprops=dict(arrowstyle="-", color=ORANGE, linewidth=1.2),
    )

    # Monday-discovery annotation, near the peak.
    ax.annotate(
        cfg["monday_label"],
        xy=(MONDAY_DISCOVERY_DAY, SERIES_COUNT[MONDAY_DISCOVERY_DAY]),
        xytext=(8.3, 6_400_000),
        fontsize=13, style="italic", color=RED, ha="left", va="bottom",
        arrowprops=dict(arrowstyle="-", color=RED, linewidth=1.2),
    )

    # Remediation-phases annotation, pointing at the low point.
    ax.annotate(
        cfg["remediation_label"],
        xy=(REMEDIATION_DAY, SERIES_COUNT[REMEDIATION_DAY]),
        xytext=(17.2, 900_000),
        fontsize=13, style="italic", color=GREEN, ha="left", va="bottom",
        arrowprops=dict(arrowstyle="-", color=GREEN, linewidth=1.2),
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-cardinality{cfg['suffix']}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=FIG_BG, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    targets = sys.argv[1:] or ["en"]
    if targets == ["all"]:
        targets = list(LANGUAGES.keys())
    for t in targets:
        if t not in LANGUAGES:
            raise SystemExit(f"unknown language {t!r}, known: {list(LANGUAGES)}")
        render(t)
