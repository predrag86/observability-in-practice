#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-suppression" chart used in
Poglavlje 14 / Chapter 14 (kad-alarm-cuti / when-the-alert-stays-silent).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-suppression.png was hand-built with no source file, so it could
not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_suppression.py sr   # -> docs/diagrams/dashboard-suppression.png
    python3 scripts/diagrams/dashboard_suppression.py en   # -> docs/diagrams/dashboard-suppression.en.png
    python3 scripts/diagrams/dashboard_suppression.py all  # both

Data note: illustrative figures reproducing the shape of the original
suppression chart — 19 job failures spread across a 17-hour window, each
one drawn as a lone bar of height 1 at the hour it happened. Every failure
individually sits under the anti-spam mechanism's "3 in 30 minutes"
threshold (no two failures ever land within 30 minutes of each other), so
every single one is suppressed and none is ever sent to the alert channel
— the "19 failures / 0 sent" finding described in the surrounding chapter
text.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

# 19 failures spread across a 17-hour window. Spacing is irregular but
# every gap between consecutive failures stays well above 30 minutes
# (0.5h), so no pair of failures ever falls inside the "3 in 30 minutes"
# suppression window -- every failure is suppressed on its own.
rng = np.random.default_rng(14)
gaps = rng.uniform(0.65, 0.95, size=18)  # hours between consecutive failures
FAILURE_HOURS = np.concatenate([[0.0], np.cumsum(gaps)])
assert len(FAILURE_HOURS) == 19
assert FAILURE_HOURS[-1] <= 17.0

TOTAL_FAILURES = 19
THRESHOLD_TEXT_COUNT = 3
THRESHOLD_TEXT_WINDOW_MIN = 30
WINDOW_HOURS = 17

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-suppression.png (default locale, no suffix)
        "title": f"Padovi zadatka po satu — svi potisnuti, nijedan poslat ({WINDOW_HOURS} sati)",
        "xlabel": "sat",
        "ylabel": "broj padova",
        "legend_suppressed": "potisnuto (repeat-gate)",
        "legend_sent": "poslato u kanal",
        "annotation": (
            f"{TOTAL_FAILURES} padova ukupno · prag mehanizma = "
            f"{THRESHOLD_TEXT_COUNT} u {THRESHOLD_TEXT_WINDOW_MIN} min\n"
            "nijedan par padova nije dovoljno blizu da ga dostigne"
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-suppression.en.png
        "title": f"Job failures per hour — all suppressed, none sent ({WINDOW_HOURS} hours)",
        "xlabel": "hour",
        "ylabel": "number of failures",
        "legend_suppressed": "suppressed (repeat-gate)",
        "legend_sent": "sent to channel",
        "annotation": (
            f"{TOTAL_FAILURES} failures total · mechanism threshold = "
            f"{THRESHOLD_TEXT_COUNT} in {THRESHOLD_TEXT_WINDOW_MIN} min\n"
            "no pair of failures is close enough together to reach it"
        ),
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
ORANGE = "#EB6834"
GREEN = "#1BAF7A"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(11.4, 4.9), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    ax.bar(
        FAILURE_HOURS, np.ones(TOTAL_FAILURES),
        width=0.12, color=ORANGE, zorder=3,
    )
    # No failure was ever sent -- there is no data series to draw for it,
    # so its legend entry is built as an explicit color swatch (a bare
    # `ax.bar([], [])` produces no patch for the legend to pick a color
    # from, and silently falls back to the default cycle color).
    legend_handles = [
        Patch(facecolor=ORANGE, label=cfg["legend_suppressed"]),
        Patch(facecolor=GREEN, label=cfg["legend_sent"]),
    ]

    ax.set_xlim(-0.6, 17.9)
    ax.set_ylim(0, 1.62)

    ax.xaxis.set_major_locator(FixedLocator([0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5]))
    ax.yaxis.set_major_locator(FixedLocator([0, 1]))

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

    ax.legend(
        handles=legend_handles,
        loc="upper right", frameon=False, fontsize=13.5,
        labelcolor=INK, handlelength=1.4, handleheight=1.4,
        bbox_to_anchor=(1.0, 1.05),
    )

    ax.text(
        0.6, 1.42, cfg["annotation"],
        fontsize=13.5, style="italic", color=ORANGE, va="top", ha="left",
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-suppression{cfg['suffix']}.png"
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
