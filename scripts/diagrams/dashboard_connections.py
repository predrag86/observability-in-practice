#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-connections" chart used in
Poglavlje 18 / Chapter 18 (baze-podataka / databases).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-connections.png was hand-built with no source file, so it could
not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_connections.py sr   # -> docs/diagrams/dashboard-connections.png
    python3 scripts/diagrams/dashboard_connections.py en   # -> docs/diagrams/dashboard-connections.en.png
    python3 scripts/diagrams/dashboard_connections.py all  # both

Data note: illustrative two-panel comparison over a 48-hour window. Left
panel is the internal postgres_exporter view — count of sessions stuck in
'idle in transaction', a slow, noisy but unmistakable linear climb visible
from hour 0. Right panel is the external CloudWatch write-latency view over
the same 48 hours — flat and unremarkable until roughly hour 40, when
latency finally starts climbing. The ~40-hour gap between the two panels is
the "40h before latency reacts" point made in the surrounding chapter text.
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

rng = np.random.default_rng(18)

HOURS = np.linspace(0, 48, 480)

# Left panel: idle-in-transaction session count, a steady linear climb from
# hour 0 (roughly 3 -> 23 sessions) with realistic noise.
SESSIONS_BASE = 3 + HOURS * (20 / 48)
SESSIONS = SESSIONS_BASE + rng.normal(0, 1.1, size=HOURS.shape)
SESSIONS = np.clip(SESSIONS, 0.3, None)

# Right panel: write latency (ms) -- flat and quiet for the first ~40 hours,
# then climbs sharply once the connection leak finally exhausts the pool.
_excess = np.clip(HOURS - 38, 0, None)
LATENCY_BASE = np.where(
    HOURS < 38,
    12.0,
    12.0 + (_excess ** 2.6) * 0.028,
)
LATENCY = LATENCY_BASE + rng.normal(0, 1.4, size=HOURS.shape)
LATENCY = np.clip(LATENCY, 6, None)

REACT_HOUR = 40

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-connections.png (default locale, no suffix)
        "title_left": "postgres_exporter (iznutra) — sesije 'idle in transaction'",
        "title_right": "CloudWatch (spolja) — latencija upisa",
        "xlabel": "sati",
        "ylabel_left": "broj sesija",
        "ylabel_right": "latencija (ms)",
        "annotation_left": (
            "trend vidljiv od sata 0\n"
            "— 40h pre nego što\n"
            "latencija reaguje"
        ),
        "annotation_right": (
            "spoljna ravan\n"
            "tek OVDE primeti\n"
            "da nešto nije u redu"
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-connections.en.png
        "title_left": "postgres_exporter (internal) — 'idle in transaction' sessions",
        "title_right": "CloudWatch (external) — write latency",
        "xlabel": "hours",
        "ylabel_left": "number of sessions",
        "ylabel_right": "latency (ms)",
        "annotation_left": (
            "trend visible from hour 0\n"
            "— 40h before latency\n"
            "reacts"
        ),
        "annotation_right": (
            "the external layer\n"
            "only notices something\n"
            "is wrong HERE"
        ),
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
ORANGE = "#EB6834"
BLUE = "#2A78D6"
RED = "#E34948"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(16.6, 5.1), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    fig.subplots_adjust(wspace=0.28)

    # --- left panel: idle-in-transaction sessions -------------------------
    ax_l.set_facecolor(AX_BG)
    ax_l.fill_between(HOURS, 0, SESSIONS, color=ORANGE, alpha=0.10, zorder=1)
    ax_l.plot(HOURS, SESSIONS, color=ORANGE, linewidth=2.0, zorder=3)
    ax_l.axvline(REACT_HOUR, color="#4A4A4A", linestyle=(0, (4, 3)), linewidth=1.3, zorder=2)

    ax_l.set_xlim(0, 48)
    ax_l.set_ylim(0, 25)
    ax_l.xaxis.set_major_locator(FixedLocator([0, 10, 20, 30, 40]))
    ax_l.yaxis.set_major_locator(FixedLocator([0, 5, 10, 15, 20]))
    ax_l.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    ax_l.set_axisbelow(True)
    for spine in ("top", "right"):
        ax_l.spines[spine].set_visible(False)
    ax_l.spines["left"].set_color(INK)
    ax_l.spines["bottom"].set_color(INK)
    ax_l.spines["left"].set_linewidth(1.0)
    ax_l.spines["bottom"].set_linewidth(1.0)
    ax_l.tick_params(axis="both", labelsize=12.5, colors=INK, length=0)

    ax_l.set_xlabel(cfg["xlabel"], fontsize=14, color=INK, labelpad=10)
    ax_l.set_ylabel(cfg["ylabel_left"], fontsize=14, color=INK, labelpad=10)
    ax_l.set_title(cfg["title_left"], fontsize=15.5, fontweight="bold", color=INK, loc="left", pad=14)

    ax_l.text(
        1.0, 23.6, cfg["annotation_left"],
        fontsize=12.5, style="italic", color=ORANGE, va="top", ha="left",
    )

    # --- right panel: write latency ---------------------------------------
    ax_r.set_facecolor(AX_BG)
    ax_r.plot(HOURS, LATENCY, color=BLUE, linewidth=2.0, zorder=3)
    ax_r.axvline(REACT_HOUR, color=RED, linestyle=(0, (4, 3)), linewidth=1.3, zorder=2)

    ax_r.set_xlim(0, 48)
    ax_r.set_ylim(5, 56)
    ax_r.xaxis.set_major_locator(FixedLocator([0, 10, 20, 30, 40]))
    ax_r.yaxis.set_major_locator(FixedLocator([10, 20, 30, 40, 50]))
    ax_r.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    ax_r.set_axisbelow(True)
    for spine in ("top", "right"):
        ax_r.spines[spine].set_visible(False)
    ax_r.spines["left"].set_color(INK)
    ax_r.spines["bottom"].set_color(INK)
    ax_r.spines["left"].set_linewidth(1.0)
    ax_r.spines["bottom"].set_linewidth(1.0)
    ax_r.tick_params(axis="both", labelsize=12.5, colors=INK, length=0)

    ax_r.set_xlabel(cfg["xlabel"], fontsize=14, color=INK, labelpad=10)
    ax_r.set_ylabel(cfg["ylabel_right"], fontsize=14, color=INK, labelpad=10)
    ax_r.set_title(cfg["title_right"], fontsize=15.5, fontweight="bold", color=INK, loc="left", pad=14)

    ax_r.text(
        41.2, 33, cfg["annotation_right"],
        fontsize=12.5, style="italic", color=RED, va="top", ha="left",
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-connections{cfg['suffix']}.png"
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
