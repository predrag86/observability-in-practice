#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-completeness" chart used in
Poglavlje 23 / Chapter 23 (batch-etl-flota / batch-etl-fleet).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-completeness.png was hand-built with no source file, so it
could not be re-rendered in English. This script reconstructs it from
one parameterized source so both language variants come from the same
data.

Usage
-----
    python3 scripts/diagrams/dashboard_completeness.py sr   # -> docs/diagrams/dashboard-completeness.png
    python3 scripts/diagrams/dashboard_completeness.py en   # -> docs/diagrams/dashboard-completeness.en.png
    python3 scripts/diagrams/dashboard_completeness.py all  # both

Data note: illustrative daily row-count for one scheduled job over 30
days, reproducing the two invisible-to-the-naked-eye failure modes the
surrounding chapter's completeness model calls out: two days the job
never started at all (days 4 and 17, "nije pokrenut" / "did not run"),
and three days it completed successfully but produced zero rows (days
11, 24 and 25, "USPEŠNO, 0 redova" / "SUCCEEDED, 0 rows"). All other
days ran and produced a plausible, noisy row count.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

# day -> rows produced, for every day the job actually ran and emitted rows.
ROWS_BY_DAY = {
    1: 4560, 2: 4430, 3: 4240,
    5: 1090, 6: 4200, 7: 4750, 8: 1900, 9: 1510, 10: 1130,
    12: 4770, 13: 3330, 14: 3370, 15: 4110, 16: 810,
    18: 4620, 19: 1350, 20: 4930, 21: 4370, 22: 1980, 23: 2810,
    26: 1140, 27: 3560, 28: 2640, 29: 2240, 30: 4230,
}
NOT_RUN_DAYS = [4, 17]
ZERO_ROWS_DAYS = [11, 24, 25]
TOTAL_DAYS = 30

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-completeness.png (default locale, no suffix)
        "title": "Dnevno izvršavanje zakazanog zadatka — 30 dana",
        "xlabel": "dan",
        "ylabel": "proizvedeno redova",
        "not_run_label": "nije\npokrenut",
        "zero_rows_label": "USPEŠNO,\n0 redova",
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-completeness.en.png
        "title": "Daily runs of the scheduled job — 30 days",
        "xlabel": "day",
        "ylabel": "rows produced",
        "not_run_label": "did not\nrun",
        "zero_rows_label": "SUCCEEDED,\n0 rows",
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
RED = "#E34948"
GREEN = "#1BAF7A"
GRAY = "#6C6C6C"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(12.4, 4.9), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    days = list(ROWS_BY_DAY.keys())
    values = list(ROWS_BY_DAY.values())
    ax.bar(days, values, width=0.68, color=GREEN, zorder=3)

    ax.set_xlim(0, 31)
    ax.set_ylim(0, 5150)

    ax.xaxis.set_major_locator(FixedLocator([0, 5, 10, 15, 20, 25, 30]))
    ax.yaxis.set_major_locator(FixedLocator([0, 1000, 2000, 3000, 4000, 5000]))

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

    for day in NOT_RUN_DAYS:
        ax.text(
            day, 40, cfg["not_run_label"],
            rotation=90, fontsize=11.5, color=GRAY, ha="center", va="bottom",
        )
    for day in ZERO_ROWS_DAYS:
        ax.text(
            day, 40, cfg["zero_rows_label"],
            rotation=90, fontsize=11.5, style="italic", color=RED, ha="center", va="bottom",
        )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-completeness{cfg['suffix']}.png"
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
