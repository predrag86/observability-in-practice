#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-sampling" chart used in
Poglavlje 12 / Chapter 12 (sampling-trejsova / trace sampling).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-sampling.png was hand-built with no source file, so it could not
be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_sampling.py sr   # -> docs/diagrams/dashboard-sampling.png
    python3 scripts/diagrams/dashboard_sampling.py en   # -> docs/diagrams/dashboard-sampling.en.png
    python3 scripts/diagrams/dashboard_sampling.py all  # both

Data note: illustrative 30-day trace *retention rate* (the fraction of
traces the collector/vendor actually kept, versus the sampling rate
configured in policy). A flat dashed line marks the expected 10% from
policy; the measured rate tracks it closely except for a ~10-day window
(days 12-22) where it drifts up to ~16%, is reported to the vendor, and the
sampling configuration is deliberately left unchanged until the mismatch
is understood -- the "reported to the vendor, config not touched" callout
described in the surrounding chapter text.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

DAYS = list(range(30))

MEASURED = [
    10.4, 10.7, 9.0, 10.0, 10.4, 10.6, 10.3, 10.6, 10.1, 10.2,
    10.1, 9.5, 9.7, 10.9, 11.2, 12.7, 13.4, 14.3, 14.3, 15.6,
    15.4, 16.2, 10.1, 10.1, 10.4, 10.0, 10.5, 9.7, 10.0, 9.8,
]

EXPECTED = 10.0

MISMATCH_START = 12
MISMATCH_END = 22

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-sampling.png (default locale, no suffix)
        "title": "Stopa zadržavanja trejsova — očekivano naspram izmerenog, 30 dana",
        "xlabel": "dan",
        "ylabel": "% zadržanih trejsova",
        "expected_label": "očekivano (iz politika)",
        "measured_label": "izmereno",
        "annotation": (
            "neslaganje prijavljeno\n"
            "dobavljaču — konfiguracija\n"
            "NIJE menjana"
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-sampling.en.png
        "title": "Trace retention rate — expected versus measured, 30 days",
        "xlabel": "day",
        "ylabel": "% of traces retained",
        "expected_label": "expected (from policy)",
        "measured_label": "measured",
        "annotation": (
            "mismatch reported to\n"
            "the vendor — config\n"
            "NOT touched"
        ),
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
BLUE = "#2A78D6"
GRAY = "#4A4A4A"
FILL = "#FCF1D9"
GOLD = "#8A6D00"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(11.4, 6.1), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    ax.axvspan(MISMATCH_START, MISMATCH_END, facecolor=FILL, edgecolor="none", zorder=1)

    ax.axhline(EXPECTED, color=GRAY, linestyle=(0, (6, 4)), linewidth=1.6,
                label=cfg["expected_label"], zorder=2)
    ax.plot(DAYS, MEASURED, color=BLUE, linewidth=2.4, marker="o", markersize=6,
             label=cfg["measured_label"], zorder=3)

    ax.set_xlim(-0.6, 29.6)
    ax.set_ylim(0, 20)

    ax.xaxis.set_major_locator(FixedLocator(range(0, 26, 5)))
    ax.yaxis.set_major_locator(FixedLocator(range(0, 21, 5)))
    ax.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    ax.set_axisbelow(True)

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(1.0)

    ax.tick_params(axis="both", labelsize=13, colors=INK, length=0)

    ax.set_xlabel(cfg["xlabel"], fontsize=14.5, color=INK, labelpad=12)
    ax.set_ylabel(cfg["ylabel"], fontsize=14.5, color=INK, labelpad=12)

    ax.set_title(cfg["title"], fontsize=19, fontweight="bold", color=INK, loc="left", pad=16)

    legend = ax.legend(
        loc="upper left", frameon=False, fontsize=14.5,
        bbox_to_anchor=(0.0, 1.0), handlelength=2.0,
    )
    for text in legend.get_texts():
        text.set_color(INK)

    ax.text(
        MISMATCH_START + 0.6, 19.2, cfg["annotation"],
        fontsize=13, style="italic", color=GOLD, va="top", ha="left",
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-sampling{cfg['suffix']}.png"
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
