#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-synthetic" chart used in
Poglavlje 9 / Chapter 9 (sinteticko-pracenje / synthetic-monitoring).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-synthetic.png was hand-built with no source file, so it could
not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_synthetic.py sr   # -> docs/diagrams/dashboard-synthetic.png
    python3 scripts/diagrams/dashboard_synthetic.py en   # -> docs/diagrams/dashboard-synthetic.en.png
    python3 scripts/diagrams/dashboard_synthetic.py all  # both

Data note: illustrative synthetic-probe latency over a 24-hour window for
three probe regions (Region A / Region B / Region C), sampled every six
minutes. All three regions share the same rough diurnal shape (a rise
through the morning, a broad midday hump, then a gradual decline) but sit
at different baseline latencies -- Region B highest, Region A in the
middle, Region C lowest -- matching the original chart. A short pink-shaded
window in the middle of the day marks a regional network problem in which
Region B's probes stop reporting entirely (a gap in the orange line) while
Region A and Region C continue reporting normally straight through it --
the "one region goes quiet while the other two keep reporting" finding
described in the surrounding chapter text.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

# 24-hour window, sampled every 6 minutes.
T = np.linspace(0, 24, 241)

# Shared diurnal shape: a bump centered mid-morning, then a gradual decline
# through the rest of the day. All three regions ride the same shape,
# offset by a different baseline latency.
_SHAPE = 14.0 * np.exp(-0.5 * ((T - 6.0) / 4.2) ** 2) - 0.35 * np.maximum(T - 11.0, 0.0)

rng = np.random.default_rng(9)
REGION_A = 183.0 + _SHAPE + rng.normal(0, 5.0, T.size)
REGION_B = 205.0 + _SHAPE + rng.normal(0, 5.5, T.size)
REGION_C = 170.0 + _SHAPE + rng.normal(0, 5.0, T.size)

# Region B goes dark for a short window in the middle of the day -- a
# regional network problem that only affects that probe region. Region A
# and Region C are left untouched and keep reporting straight through it.
GAP_START, GAP_END = 11.4, 12.3
_gap_mask = (T >= GAP_START) & (T <= GAP_END)
REGION_B_WITH_GAP = REGION_B.copy()
REGION_B_WITH_GAP[_gap_mask] = np.nan

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-synthetic.png (default locale, no suffix)
        "title": "Sintetičko praćenje — latencija po regionu probe, danas",
        "xlabel": "sat (danas)",
        "ylabel": "latencija (ms)",
        "region_labels": {"a": "Region A", "b": "Region B", "c": "Region C"},
        "annotation": (
            "Region B: probe ne javlja\n"
            "(regionalni mrežni problem,\n"
            "A i C i dalje rade)"
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-synthetic.en.png
        "title": "Synthetic monitoring — latency by probe region, today",
        "xlabel": "hour (today)",
        "ylabel": "latency (ms)",
        "region_labels": {"a": "Region A", "b": "Region B", "c": "Region C"},
        "annotation": (
            "Region B: probes not reporting\n"
            "(regional network problem,\n"
            "A and C still working)"
        ),
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
BLUE = "#2A78D6"
ORANGE = "#EB6834"
GREEN = "#1BAF7A"
RED = "#E34948"
PINK_FILL = "#FCECEC"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(12.4, 4.6), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    ax.axvspan(GAP_START, GAP_END, facecolor=PINK_FILL, edgecolor="none", zorder=1)

    ax.plot(T, REGION_A, color=BLUE, linewidth=1.6, zorder=3,
             label=cfg["region_labels"]["a"])
    ax.plot(T, REGION_B_WITH_GAP, color=ORANGE, linewidth=1.6, zorder=3,
             label=cfg["region_labels"]["b"])
    ax.plot(T, REGION_C, color=GREEN, linewidth=1.6, zorder=3,
             label=cfg["region_labels"]["c"])

    ax.set_xlim(-0.3, 24.3)
    ax.set_ylim(135, 250)

    ax.xaxis.set_major_locator(FixedLocator([0, 5, 10, 15, 20]))
    ax.yaxis.set_major_locator(FixedLocator([140, 160, 180, 200, 220]))

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
        loc="upper left", frameon=False, fontsize=14,
        labelcolor=INK, handlelength=1.6,
        bbox_to_anchor=(0.005, 1.02),
    )

    # Leader-line annotation pointing at the Region B gap.
    ax.annotate(
        cfg["annotation"],
        xy=(GAP_END + 0.1, 214),
        xytext=(13.6, 241),
        fontsize=13, style="italic", color=RED, va="top", ha="left",
        arrowprops=dict(arrowstyle="-", color=RED, linewidth=1.2,
                         connectionstyle="arc3,rad=0"),
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-synthetic{cfg['suffix']}.png"
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
