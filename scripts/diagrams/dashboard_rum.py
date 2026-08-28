#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-rum" chart used in
Poglavlje 8 / Chapter 8 (frontend-rum).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-rum.png was hand-built with no source file, so it could not be
re-rendered in English. This script reconstructs it from one parameterized
source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_rum.py sr   # -> docs/diagrams/dashboard-rum.png
    python3 scripts/diagrams/dashboard_rum.py en   # -> docs/diagrams/dashboard-rum.en.png
    python3 scripts/diagrams/dashboard_rum.py all  # both

Data note: illustrative 14-day RUM series for Largest Contentful Paint
(LCP), shown as p50 / p75 / p95 in seconds. p50 and p75 stay flat and
mostly under/around the 2.5s "good" threshold; p95 spikes sharply on day 9
(a regression confined to one geographic region), which is the callout the
surrounding chapter text refers to.
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

rng = np.random.default_rng(8)

DAYS = np.arange(14)

P50 = np.clip(1.82 + rng.normal(0, 0.075, size=14), None, None)
P50[8] = 1.65
P50[9] = 1.83

P75 = np.clip(2.42 + rng.normal(0, 0.09, size=14), None, None)
P75[1] = 2.33
P75[2] = 2.58
P75[4] = 2.57

# p95: normal noisy band around ~3.4-3.7s, with a sharp one-day spike to
# ~5.0s on day 9 (single-region regression), recovering by day 10.
P95 = 3.5 + rng.normal(0, 0.12, size=14)
P95[4] = 3.75
P95[8] = 3.10
P95[9] = 5.00
P95[10] = 3.27
P95[11] = 3.24

GOOD_THRESHOLD = 2.5

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-rum.png (default locale, no suffix)
        "title": "RUM — Largest Contentful Paint (LCP), p50 / p75 / p95, 14 dana",
        "xlabel": "dan",
        "ylabel": "sekunde",
        "series_labels": {"p50": "p50", "p75": "p75", "p95": "p95"},
        "threshold_label": '"dobar" prag (2.5s)',
        "annotation": "regresija u jednom\ngeografskom regionu",
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-rum.en.png
        "title": "RUM — Largest Contentful Paint (LCP), p50 / p75 / p95, 14 days",
        "xlabel": "day",
        "ylabel": "seconds",
        "series_labels": {"p50": "p50", "p75": "p75", "p95": "p95"},
        "threshold_label": '"good" threshold (2.5s)',
        "annotation": "regression confined to\none geographic region",
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
GREEN = "#1BAF7A"
BLUE = "#2A78D6"
RED = "#E34948"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(11.4, 6.1), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    ax.plot(DAYS, P50, color=GREEN, linewidth=2.2, marker="o", markersize=6,
             label=cfg["series_labels"]["p50"], zorder=3)
    ax.plot(DAYS, P75, color=BLUE, linewidth=2.2, marker="o", markersize=6,
             label=cfg["series_labels"]["p75"], zorder=3)
    ax.plot(DAYS, P95, color=RED, linewidth=2.2, marker="o", markersize=6,
             label=cfg["series_labels"]["p95"], zorder=3)

    ax.axhline(GOOD_THRESHOLD, color="#4A4A4A", linestyle=(0, (4, 3)), linewidth=1.3, zorder=2)
    ax.text(0.15, GOOD_THRESHOLD + 0.06, cfg["threshold_label"],
             fontsize=12.5, style="italic", color="#4A4A4A", ha="left", va="bottom")

    ax.set_xlim(-0.4, 13.4)
    ax.set_ylim(1.4, 5.35)

    ax.xaxis.set_major_locator(FixedLocator(range(0, 14, 2)))
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
        loc="upper left", frameon=False, fontsize=14.5, ncol=3,
        bbox_to_anchor=(0.0, 1.0), handlelength=1.6, columnspacing=1.6,
    )
    for text in legend.get_texts():
        text.set_color(INK)

    # Leader-line annotation pointing at the p95 spike on day 9.
    ax.annotate(
        cfg["annotation"],
        xy=(9, P95[9]),
        xytext=(10.3, 4.55),
        fontsize=13.5, style="italic", color=RED, va="center", ha="left",
        arrowprops=dict(arrowstyle="-", color=RED, linewidth=1.2,
                         connectionstyle="arc3,rad=0.15"),
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-rum{cfg['suffix']}.png"
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
