#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-alarm-audit" chart used in
Poglavlje 29 / Chapter 29 (fazni-rollout / phased-rollout).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-alarm-audit.png was hand-built with no source file, so it could
not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_alarm_audit.py sr   # -> docs/diagrams/dashboard-alarm-audit.png
    python3 scripts/diagrams/dashboard_alarm_audit.py en   # -> docs/diagrams/dashboard-alarm-audit.en.png
    python3 scripts/diagrams/dashboard_alarm_audit.py all  # both

Data note: illustrative figures reproducing the shape of the original audit
chart — 23 legacy per-family alerts, sorted by "days since last data point".
7 alerts are recently active (short green bars); 16 have received nothing
for well over a year (long red bars, clustered around 370-430 days), which
is the "16 of 23" callout in the surrounding chapter text.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

rng = np.random.default_rng(29)

# 7 alerts still receiving data recently (small "days since last point").
ACTIVE_DAYS = np.sort(rng.uniform(1, 27, size=7))

# 16 alerts stale for well over a year.
STALE_DAYS = rng.uniform(365, 432, size=16)
STALE_DAYS[-1] = 400  # last bar (bottom) sits near the "1 year" line's right side

ONE_YEAR = 365

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-alarm-audit.png (default locale, no suffix)
        "title": "Revizija starih alarma po porodici zadataka — dana od poslednje tačke podataka",
        "xlabel": "dana od poslednje primljene tačke podataka",
        "ylabel": "23 alarma po porodici zadataka (sortirano)",
        "one_year_label": "1 godina",
        "annotation": (
            "16 od 23 — nula podataka preko godinu dana\n"
            "(izgledali 'zeleno' jer 'nema podataka = OK')"
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-alarm-audit.en.png
        "title": "Audit of old alerts by task family — days since last data point",
        "xlabel": "days since last received data point",
        "ylabel": "23 alerts by task family (sorted)",
        "one_year_label": "1 year",
        "annotation": (
            "16 of 23 — zero data for over a year\n"
            "(they looked 'green' only because 'no data = OK')"
        ),
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
RED = "#E34948"
GREEN = "#1BAF7A"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(11.2, 5.1), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    # Bars are drawn top-to-bottom in the original: active (green) bars on
    # top, stale (red) bars below. barh with increasing y draws bottom-up,
    # so we invert the y-axis to get that ordering.
    n_active = len(ACTIVE_DAYS)
    n_stale = len(STALE_DAYS)
    n_total = n_active + n_stale
    y_positions = np.arange(n_total)

    values = np.concatenate([ACTIVE_DAYS, STALE_DAYS])
    colors = [GREEN] * n_active + [RED] * n_stale

    ax.barh(y_positions, values, color=colors, height=0.62, zorder=3)

    ax.invert_yaxis()
    ax.set_ylim(n_total - 0.4, -0.6)
    ax.set_xlim(0, 450)
    ax.set_yticks([])

    ax.xaxis.set_major_locator(FixedLocator([0, 100, 200, 300, 400]))
    ax.grid(True, which="major", axis="x", color=GRID, linewidth=1.0, zorder=0)
    ax.set_axisbelow(True)

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(1.0)

    ax.tick_params(axis="x", labelsize=13, colors=INK, length=0)
    ax.tick_params(axis="y", length=0)

    # "1 year" reference line
    ax.axvline(ONE_YEAR, color="#4A4A4A", linestyle=(0, (4, 3)), linewidth=1.3, zorder=2)
    ax.text(
        ONE_YEAR + 22, n_total - 1.55, cfg["one_year_label"],
        fontsize=11.5, color="#4A4A4A", ha="left", va="bottom",
    )

    ax.set_xlabel(cfg["xlabel"], fontsize=14.5, color=INK, labelpad=12)
    ax.set_ylabel(cfg["ylabel"], fontsize=14.5, color=INK, labelpad=12)

    ax.set_title(cfg["title"], fontsize=18, fontweight="bold", color=INK, loc="left", pad=16)

    ax.text(
        95, 0.35, cfg["annotation"],
        fontsize=13.5, style="italic", color=RED, va="top", ha="left",
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-alarm-audit{cfg['suffix']}.png"
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
