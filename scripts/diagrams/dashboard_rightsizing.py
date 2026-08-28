#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-rightsizing" chart used in
Poglavlje 19 / Chapter 19 (samostalni-klaster / self-managed-cluster).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-rightsizing.png was hand-built with no source file, so it could
not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_rightsizing.py sr   # -> docs/diagrams/dashboard-rightsizing.png
    python3 scripts/diagrams/dashboard_rightsizing.py en   # -> docs/diagrams/dashboard-rightsizing.en.png
    python3 scripts/diagrams/dashboard_rightsizing.py all  # both

Data note: illustrative queries-in-flight measurement over a full 7-day
(168h) window for a self-managed Dremio-type cluster, taken to check
whether an automatic-shutdown-on-idle lever would ever actually fire. The
series oscillates daily between roughly 5 and 11 queries/min and never
comes close to the "truly idle" threshold of 0.5 queries/min drawn as a
reference line — the measured basis for the chapter's point that this
particular lever has no real window to operate in.
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

rng = np.random.default_rng(19)

HOURS = np.linspace(0, 168, 700)  # 7 days, ~14.4 min resolution

daily = 7.9 + 2.6 * np.sin(2 * np.pi * (HOURS - 7) / 24)
noise = rng.normal(0, 0.55, size=HOURS.size)
# small high-frequency jitter on top, like the original's jagged texture
jitter = 0.35 * np.sin(2 * np.pi * HOURS / 1.7 + rng.uniform(0, 6.28))
QUERIES = np.clip(daily + noise + jitter, 4.3, 11.3)

IDLE_THRESHOLD = 0.5

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-rightsizing.png (default locale, no suffix)
        "title": 'Upiti u toku — klaster, 7 dana (tražen prozor neaktivnosti)',
        "xlabel": "sati (7 dana)",
        "ylabel": "upita/min",
        "annotation": (
            'prag "stvarno neaktivno" (0.5 upita/min)\n'
            "— nikad dostignut kroz cele 7 dana"
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-rightsizing.en.png
        "title": 'Queries in flight — cluster, 7 days (searching for an idle window)',
        "xlabel": "hours (7 days)",
        "ylabel": "queries/min",
        "annotation": (
            'the "truly idle" threshold (0.5 queries/min)\n'
            "— never reached across the full 7 days"
        ),
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
GREEN = "#1BAF7A"
RED = "#E34948"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(12.9, 4.8), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    ax.fill_between(HOURS, QUERIES, color=GREEN, alpha=0.14, zorder=1)
    ax.plot(HOURS, QUERIES, color=GREEN, linewidth=1.8, zorder=3)

    ax.axhline(IDLE_THRESHOLD, color=RED, linestyle=(0, (5, 3)), linewidth=1.6, zorder=2)

    ax.set_xlim(0, 168)
    ax.set_ylim(0, 12)
    ax.xaxis.set_major_locator(FixedLocator(range(0, 169, 20)))

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

    ax.text(
        2, IDLE_THRESHOLD + 1.05, cfg["annotation"],
        fontsize=13, style="italic", color=RED, va="bottom", ha="left",
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-rightsizing{cfg['suffix']}.png"
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
