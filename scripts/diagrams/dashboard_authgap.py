#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-authgap" chart used in
Poglavlje 20 / Chapter 20 (autentikacija-iam / authentication-iam).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-authgap.png was hand-built with no source file, so it could not
be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_authgap.py sr   # -> docs/diagrams/dashboard-authgap.png
    python3 scripts/diagrams/dashboard_authgap.py en   # -> docs/diagrams/dashboard-authgap.en.png
    python3 scripts/diagrams/dashboard_authgap.py all  # both

Data note: illustrative daily counts of visible login events over a
14-day window, log scale. Failed logins (a few dozen a day) were always
visible. Successful logins were never logged at all until the log level
was raised on day 7 -- after which thousands a day suddenly appear, not
because logins increased, but because they finally started being
recorded.
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

rng = np.random.default_rng(20)

DAYS = np.arange(0, 14)
CUTOVER_DAY = 6.5  # log level raised between day 6 and day 7

FAILED = rng.integers(30, 51, size=len(DAYS))
SUCCESS = np.full(len(DAYS), np.nan)
SUCCESS[DAYS >= 7] = rng.integers(2450, 3050, size=(DAYS >= 7).sum())

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-authgap.png (default locale, no suffix)
        "title": "Vidljivi događaji prijave po danu — pre/posle podizanja nivoa loga",
        "xlabel": "dan",
        "ylabel": "broj vidljivih događaja (log skala)",
        "legend_failed": "neuspeli (uvek vidljivi)",
        "legend_success": "uspešni (vidljivi tek od dana 7)",
        "annotation": "dan 7: nivo loga podignut\n— uspesi postaju vidljivi",
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-authgap.en.png
        "title": "Visible login events per day — before/after raising the log level",
        "xlabel": "day",
        "ylabel": "number of visible events (log scale)",
        "legend_failed": "failed (always visible)",
        "legend_success": "successful (visible only from day 7)",
        "annotation": "day 7: log level raised\n— successes become visible",
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
RED = "#E34948"
GREEN = "#1BAF7A"

YMIN = 0.6


def yfmt(v, _pos):
    if v < 0.9:
        return "0"
    exp = int(round(np.log10(v)))
    return f"$10^{{{exp}}}$"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(11.5, 4.5), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    width = 0.38
    ax.bar(
        DAYS - width / 2, FAILED, width=width, bottom=YMIN,
        color=RED, label=cfg["legend_failed"], zorder=3,
    )
    mask = ~np.isnan(SUCCESS)
    ax.bar(
        DAYS[mask] + width / 2, SUCCESS[mask], width=width, bottom=YMIN,
        color=GREEN, label=cfg["legend_success"], zorder=3,
    )

    ax.axvline(CUTOVER_DAY, color="#4A4A4A", linestyle=(0, (4, 3)), linewidth=1.3, zorder=2)

    ax.set_yscale("log")
    ax.set_ylim(YMIN, 4000)
    ax.set_xlim(-0.8, 13.8)

    ax.yaxis.set_major_locator(FixedLocator([YMIN, 1, 10, 100, 1000]))
    ax.yaxis.set_major_formatter(FuncFormatter(yfmt))
    ax.xaxis.set_major_locator(FixedLocator(range(0, 15, 2)))

    ax.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    ax.set_axisbelow(True)

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(1.0)

    ax.tick_params(axis="both", labelsize=13, colors=INK, length=0)

    ax.set_xlabel(cfg["xlabel"], fontsize=14.5, color=INK, labelpad=12)
    ax.set_ylabel(cfg["ylabel"], fontsize=14.5, color=INK, labelpad=10)

    ax.set_title(cfg["title"], fontsize=18, fontweight="bold", color=INK, loc="left", pad=16)

    legend = ax.legend(
        loc="upper left", frameon=False, fontsize=13.5, handlelength=1.4,
        borderaxespad=1.0,
    )
    for text in legend.get_texts():
        text.set_color(INK)

    ax.text(
        -0.5, 40, cfg["annotation"],
        fontsize=12.5, style="italic", color=GREEN, va="bottom", ha="left",
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-authgap{cfg['suffix']}.png"
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
