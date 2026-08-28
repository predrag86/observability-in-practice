#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-snowflake" chart used in
Poglavlje 24 / Chapter 24 (snowflake-servis-koji-nije-nas / "Snowflake:
a service that isn't ours").

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-snowflake.png was hand-built with no source file, so it could
not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_snowflake.py sr   # -> docs/diagrams/dashboard-snowflake.png
    python3 scripts/diagrams/dashboard_snowflake.py en   # -> docs/diagrams/dashboard-snowflake.en.png
    python3 scripts/diagrams/dashboard_snowflake.py all  # both

Data note: two stacked panels over 72 hours (3 days) of a scheduled-pull
freshness gauge for an external SaaS/warehouse table.

Top panel -- "age of last loaded row", a normal sawtooth between roughly
1.7h and 5.2h (the collector pulls a fresh batch every ~2h, and the gauge
counts up until the next pull). During hours 48-60 the collector itself is
dead: the gauge keeps counting up with no resets (a straight climb to
~16.7h) because nothing is pulling fresh rows -- it is indistinguishable
from a real, ever-widening data gap unless you also look at collector
health.

Bottom panel -- "collector_up", a simple up/down step that is 1 the whole
time except for that same 48-60h window, where it drops to 0. This is the
one signal that disambiguates "collector is dead" from "the upstream table
really is stale", which is the point the surrounding chapter text makes:
freshness alerts were gated on collector_up, so during the outage they
were silenced and only a "collector down" alert fired instead.
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

rng = np.random.default_rng(24)

PERIOD = 2.0
LOW = 1.7
HIGH = 5.2
OUTAGE_START = 48.0
OUTAGE_END = 60.0
TOTAL_HOURS = 72.0


def _sawtooth_segment(t0, t1):
    """Zig-zag (low, high) tooth pairs covering [t0, t1) at PERIOD spacing."""
    xs, ys = [], []
    t = t0
    while t < t1 - 1e-9:
        low_t = t
        high_t = min(t + PERIOD - 0.06, t1)
        low_v = LOW + rng.normal(0, 0.12)
        high_v = HIGH + rng.normal(0, 0.12)
        xs += [low_t, high_t]
        ys += [low_v, high_v]
        t += PERIOD
    return xs, ys


_x1, _y1 = _sawtooth_segment(0.0, OUTAGE_START)
_x2, _y2 = _sawtooth_segment(OUTAGE_END, TOTAL_HOURS)

AGE_X = (
    _x1
    + [OUTAGE_START, OUTAGE_END, OUTAGE_END + 0.05]
    + _x2
)
AGE_Y = (
    _y1
    + [_y1[-1], 16.7, 2.0]
    + _y2
)

UP_TIMES = [0, OUTAGE_START, OUTAGE_START, OUTAGE_END, OUTAGE_END, TOTAL_HOURS]
UP_STATES = [1, 1, 0, 0, 1, 1]

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-snowflake.png (default locale, no suffix)
        "title_top": "Starost poslednjeg učitanog reda (sati)",
        "title_bottom": "collector_up — da li je kolektor živ",
        "ylabel_top": "sati",
        "xlabel": "sati (3 dana)",
        "normal_peak_label": "normalan sawtooth vrh (~5.2h)",
        "annotation_dead": "kolektor mrtav — gauge\nse smrzava, pa \"stari\"\njer vreme prolazi",
        "annotation_gate": (
            "gejt zatvoren ovde — alarmi svežine\n"
            "UTIŠANI, javlja se samo\n"
            "\"kolektor pao\" umesto toga"
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-snowflake.en.png
        "title_top": "Age of last loaded row (hours)",
        "title_bottom": "collector_up — is the collector alive",
        "ylabel_top": "hours",
        "xlabel": "hours (3 days)",
        "normal_peak_label": "normal sawtooth peak (~5.2h)",
        "annotation_dead": "collector dead — the gauge\nfreezes, so it \"ages\"\nsimply because time passes",
        "annotation_gate": (
            "gate closed here — freshness alerts\n"
            "SILENCED, only \"collector down\"\n"
            "fires instead"
        ),
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
BLUE = "#2A78D6"
RED = "#E34948"
ORANGE = "#EB6834"
GREEN = "#1BAF7A"
GREEN_FILL = "#E3F5EE"
PINK_FILL = "#FCECEC"
GRAY = "#4A4A4A"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(11.4, 7.2), dpi=190,
        gridspec_kw={"height_ratios": [1.7, 1]},
    )
    fig.patch.set_facecolor(FIG_BG)

    # ---- top panel: age of last loaded row ----
    ax_top.set_facecolor(AX_BG)
    ax_top.axvspan(OUTAGE_START, OUTAGE_END, facecolor=PINK_FILL, edgecolor="none", zorder=1)
    ax_top.plot(AGE_X, AGE_Y, color=BLUE, linewidth=2.2, zorder=3)

    ax_top.axhline(HIGH, color=GRAY, linestyle=(0, (4, 3)), linewidth=1.2, zorder=2)
    ax_top.text(1.2, HIGH + 0.35, cfg["normal_peak_label"], fontsize=12,
                 style="italic", color=GRAY, ha="left", va="bottom")

    ax_top.set_xlim(-1, TOTAL_HOURS + 1)
    ax_top.set_ylim(0.5, 18.5)
    ax_top.xaxis.set_major_locator(FixedLocator(range(0, 71, 10)))
    ax_top.yaxis.set_major_locator(FixedLocator(range(2, 17, 2)))
    ax_top.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    ax_top.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax_top.spines[spine].set_visible(False)
    ax_top.spines["bottom"].set_color(INK)
    ax_top.spines["bottom"].set_linewidth(1.0)
    ax_top.tick_params(axis="both", labelsize=12.5, colors=INK, length=0)
    ax_top.set_ylabel(cfg["ylabel_top"], fontsize=14, color=INK, labelpad=10)
    ax_top.set_title(cfg["title_top"], fontsize=18, fontweight="bold", color=INK, loc="left", pad=14)

    ax_top.annotate(
        cfg["annotation_dead"],
        xy=(54, 11.0),
        xytext=(63, 10.3),
        fontsize=12.5, style="italic", color=RED, va="center", ha="left",
        arrowprops=dict(arrowstyle="-", color=RED, linewidth=1.1,
                         connectionstyle="arc3,rad=-0.05"),
    )

    # ---- bottom panel: collector_up ----
    ax_bot.set_facecolor(AX_BG)
    ax_bot.axvspan(OUTAGE_START, OUTAGE_END, facecolor=PINK_FILL, edgecolor="none", zorder=1)
    ax_bot.fill_between(UP_TIMES, UP_STATES, step="post", color=GREEN_FILL, zorder=2)
    ax_bot.step(UP_TIMES, UP_STATES, where="post", color=GREEN, linewidth=2.4, zorder=3)

    ax_bot.set_xlim(-1, TOTAL_HOURS + 1)
    ax_bot.set_ylim(-0.15, 1.35)
    ax_bot.xaxis.set_major_locator(FixedLocator(range(0, 71, 10)))
    ax_bot.yaxis.set_major_locator(FixedLocator([0, 1]))
    ax_bot.grid(True, which="major", axis="x", color=GRID, linewidth=1.0, zorder=0)
    ax_bot.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax_bot.spines[spine].set_visible(False)
    ax_bot.spines["bottom"].set_color(INK)
    ax_bot.spines["bottom"].set_linewidth(1.0)
    ax_bot.tick_params(axis="both", labelsize=12.5, colors=INK, length=0)
    ax_bot.set_xlabel(cfg["xlabel"], fontsize=14, color=INK, labelpad=10)
    ax_bot.set_title(cfg["title_bottom"], fontsize=18, fontweight="bold", color=INK, loc="left", pad=14)

    ax_bot.text(
        49.0, 1.28, cfg["annotation_gate"],
        fontsize=12.5, style="italic", color=ORANGE, va="top", ha="left",
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-snowflake{cfg['suffix']}.png"
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
