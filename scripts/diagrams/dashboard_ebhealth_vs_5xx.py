#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-ebhealth-vs-5xx" chart used in
Poglavlje 28 / Chapter 28 (ai-asistirana-observability / AI-assisted
observability).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-ebhealth-vs-5xx.png was hand-built with no source file, so it
could not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_ebhealth_vs_5xx.py sr   # -> docs/diagrams/dashboard-ebhealth-vs-5xx.png
    python3 scripts/diagrams/dashboard_ebhealth_vs_5xx.py en   # -> docs/diagrams/dashboard-ebhealth-vs-5xx.en.png
    python3 scripts/diagrams/dashboard_ebhealth_vs_5xx.py all  # both

Data note: illustrative two-panel comparison over a 12-hour window, sharing
the x-axis and a shaded incident window (hours 4.5-7.5). Top panel is
Elastic Beanstalk's derived 'EnvironmentHealth' failure percentage, which
swells to a seemingly alarming ~33% during the window. Bottom panel is the
authoritative ALB 5xx rate over the same window, which barely moves (peaks
around 0.028% of requests) -- the "looks like an outage, isn't one" point
made in the surrounding chapter text. Two separate y-axes are used (not a
single shared/dual axis) because that is how the original chart presents
them: as two independently-scaled panels, not one overlaid dual-axis plot.
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

rng = np.random.default_rng(28)

TIME = np.linspace(0, 12, 300)
INCIDENT_START, INCIDENT_END = 4.5, 7.5

# Smooth bump shape shared by both series: zero outside the incident window,
# a flattened peak in the middle (steep sides, plateau-ish top).
_u = np.clip((TIME - INCIDENT_START) / (INCIDENT_END - INCIDENT_START), 0, 1)
BUMP = np.where((TIME >= INCIDENT_START) & (TIME <= INCIDENT_END),
                 np.sin(np.pi * _u) ** 0.55, 0.0)

# Top panel: EnvironmentHealth-derived "failure" percentage -- flat ~2%
# baseline, swelling to ~33% during the incident window.
EB_HEALTH = 2.0 + 31.0 * BUMP + rng.normal(0, 0.7, size=TIME.shape)
EB_HEALTH = np.clip(EB_HEALTH, 0, 100)

# Bottom panel: authoritative ALB 5xx rate (% of requests) -- noisy but tiny
# throughout, with only a mild bump during the same window.
ALB_5XX = 0.0145 + 0.0075 * BUMP + rng.normal(0, 0.0035, size=TIME.shape)
ALB_5XX = np.clip(ALB_5XX, 0, None)

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-ebhealth-vs-5xx.png (default locale, no suffix)
        "title_top": "Elastic Beanstalk — 'EnvironmentHealth' izveden procenat greške",
        "title_bottom": "ALB — stvarna 5xx stopa (autoritativni izvor)",
        "xlabel": "sati",
        "ylabel_top": "% ('poboljšano zdravlje')",
        "ylabel_bottom": "% zahteva",
        "annotation_top": "~33% 'failure' —\nizgleda kao ozbiljan ispad",
        "annotation_bottom": "stvarno ~0.016% —\nkorisnici to gotovo\nnisu ni osetili",
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-ebhealth-vs-5xx.en.png
        "title_top": "Elastic Beanstalk — 'EnvironmentHealth' derived failure percentage",
        "title_bottom": "ALB — actual 5xx rate (authoritative source)",
        "xlabel": "hours",
        "ylabel_top": "% ('improved health')",
        "ylabel_bottom": "% of requests",
        "annotation_top": "~33% 'failure' —\nlooks like a serious outage",
        "annotation_bottom": "actually ~0.016% —\nusers barely felt\nit at all",
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
RED = "#E34948"
GREEN = "#1BAF7A"
PINK_FILL = "#FCECEC"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, (ax_top, ax_bottom) = plt.subplots(
        2, 1, figsize=(12.2, 6.1), dpi=190, sharex=True
    )
    fig.patch.set_facecolor(FIG_BG)

    for ax in (ax_top, ax_bottom):
        ax.set_facecolor(AX_BG)
        ax.axvspan(INCIDENT_START, INCIDENT_END, facecolor=PINK_FILL, edgecolor="none", zorder=1)
        ax.set_xlim(-0.3, 12.3)
        ax.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(INK)
        ax.spines["bottom"].set_color(INK)
        ax.spines["left"].set_linewidth(1.0)
        ax.spines["bottom"].set_linewidth(1.0)
        ax.tick_params(axis="both", labelsize=12.5, colors=INK, length=0)

    ax_top.xaxis.set_major_locator(FixedLocator(range(0, 13, 2)))
    plt.setp(ax_top.get_xticklabels(), visible=False)

    # --- top panel: EnvironmentHealth derived failure % -------------------
    ax_top.plot(TIME, EB_HEALTH, color=RED, linewidth=2.2, zorder=3)
    ax_top.set_ylim(0, 100)
    ax_top.yaxis.set_major_locator(FixedLocator([0, 20, 40, 60, 80, 100]))
    ax_top.set_ylabel(cfg["ylabel_top"], fontsize=13.5, color=INK, labelpad=10)
    ax_top.set_title(cfg["title_top"], fontsize=18, fontweight="bold", color=INK, loc="left", pad=14)

    ax_top.annotate(
        cfg["annotation_top"],
        xy=(6.0, 33.5),
        xytext=(7.7, 62),
        fontsize=13.5, style="italic", color=RED, va="bottom", ha="left",
        arrowprops=dict(arrowstyle="-", color=RED, linewidth=1.1, connectionstyle="arc3,rad=0"),
    )

    # --- bottom panel: authoritative ALB 5xx rate --------------------------
    ax_bottom.plot(TIME, ALB_5XX, color=GREEN, linewidth=1.8, zorder=3)
    ax_bottom.set_ylim(0, 0.08)
    ax_bottom.xaxis.set_major_locator(FixedLocator(range(0, 13, 2)))
    ax_bottom.yaxis.set_major_locator(FixedLocator([0, 0.02, 0.04, 0.06, 0.08]))
    ax_bottom.set_xlabel(cfg["xlabel"], fontsize=14.5, color=INK, labelpad=10)
    ax_bottom.set_ylabel(cfg["ylabel_bottom"], fontsize=13.5, color=INK, labelpad=10)
    ax_bottom.set_title(cfg["title_bottom"], fontsize=18, fontweight="bold", color=INK, loc="left", pad=14)

    ax_bottom.annotate(
        cfg["annotation_bottom"],
        xy=(6.0, 0.0285),
        xytext=(8.3, 0.053),
        fontsize=12.5, style="italic", color=GREEN, va="bottom", ha="left",
        arrowprops=dict(arrowstyle="-", color=GREEN, linewidth=1.1, connectionstyle="arc3,rad=0.15"),
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-ebhealth-vs-5xx{cfg['suffix']}.png"
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
