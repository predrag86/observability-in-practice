#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-alert-streak" chart used in
Poglavlje 30 / Chapter 30 (merenje-zrelosti / measuring-maturity).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-alert-streak.png was hand-built with no source file, so it could
not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_alert_streak.py sr   # -> docs/diagrams/dashboard-alert-streak.png
    python3 scripts/diagrams/dashboard_alert_streak.py en   # -> docs/diagrams/dashboard-alert-streak.en.png
    python3 scripts/diagrams/dashboard_alert_streak.py all  # both

Data note: illustrative step function over 16 weeks showing an alert
state (OK / IN ALERT). The alert fires around week 2.3, stays lit for
roughly ten weeks with two brief one-tick dips (a rebuild that looked
like a fix), and finally clears around week 12.4 — the "rang continuously
for ~10 weeks" finding described in the surrounding chapter text.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

# Step-function control points: (week, state) with state 0=OK, 1=IN ALERT,
# drawn with drawstyle="steps-post".
ALARM_START = 2.3
DIP_1 = (5.2, 5.3)
DIP_2 = (8.7, 8.8)
ALARM_END = 12.4

TIMES = [0, ALARM_START, DIP_1[0], DIP_1[1], DIP_2[0], DIP_2[1], ALARM_END, 16]
STATES = [0, 1, 0, 1, 0, 1, 0, 0]

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-alert-streak.png (default locale, no suffix)
        "title": "Stanje alarma 'metrika koraka prestala da stiže' — 16 nedelja",
        "xlabel": "nedelje",
        "ytick_ok": "OK",
        "ytick_alarm": "U ALARMU",
        "annotation_streak": (
            "~10 nedelja neprekidno —\n"
            "najstariji nerešen nalaz revizije,\n"
            "namerno na vrh liste"
        ),
        "annotation_dip": "kratak pad =\nrebuild koji je\nIZGLEDAO kao\npopravka",
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-alert-streak.en.png
        "title": "State of alert 'step metric stopped arriving' — 16 weeks",
        "xlabel": "weeks",
        "ytick_ok": "OK",
        "ytick_alarm": "IN ALERT",
        "annotation_streak": (
            "~10 weeks continuously —\n"
            "the oldest unresolved audit finding,\n"
            "deliberately placed at the top of the list"
        ),
        "annotation_dip": "brief dip =\na rebuild that\nLOOKED like\na fix",
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
RED = "#E34948"
PINK_FILL = "#FCECEC"
GRAY = "#7A7A7A"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(12.4, 4.4), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    ax.axvspan(ALARM_START, ALARM_END, facecolor=PINK_FILL, edgecolor="none", zorder=1)

    ax.step(TIMES, STATES, where="post", color=RED, linewidth=2.6, zorder=3)

    ax.set_xlim(0, 16)
    ax.set_ylim(-0.35, 1.85)

    ax.xaxis.set_major_locator(FixedLocator(range(0, 17, 2)))
    ax.yaxis.set_major_locator(FixedLocator([0, 1]))
    ax.set_yticklabels([cfg["ytick_ok"], cfg["ytick_alarm"]])

    ax.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    ax.set_axisbelow(True)

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(1.0)

    ax.tick_params(axis="both", labelsize=13, colors=INK, length=0)

    ax.set_xlabel(cfg["xlabel"], fontsize=14.5, color=INK, labelpad=12)

    ax.set_title(cfg["title"], fontsize=18, fontweight="bold", color=INK, loc="left", pad=16)

    # Leader-line annotation pointing at the top of the long streak.
    ax.annotate(
        cfg["annotation_streak"],
        xy=(9.6, 1.0),
        xytext=(10.6, 1.55),
        fontsize=12.5, style="italic", color=RED, va="bottom", ha="left",
        arrowprops=dict(arrowstyle="-", color=RED, linewidth=1.2,
                         connectionstyle="arc3,rad=-0.1"),
    )

    # Floating annotation near the first brief dip.
    ax.text(
        3.15, 0.42, cfg["annotation_dip"],
        fontsize=11.5, style="italic", color=GRAY, va="top", ha="left",
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-alert-streak{cfg['suffix']}.png"
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
