#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-burnrate" chart used in
Poglavlje 15 / Chapter 15 (slo-budzet-greske / slo-error-budget).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-burnrate.png was hand-built with no source file, so it could
not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_burnrate.py sr   # -> docs/diagrams/dashboard-burnrate.png
    python3 scripts/diagrams/dashboard_burnrate.py en   # -> docs/diagrams/dashboard-burnrate.en.png
    python3 scripts/diagrams/dashboard_burnrate.py all  # both

Data note: illustrative multi-window burn-rate signal over 180 minutes.
A 20-minute incident (minutes 60-80) drives the 5-minute short window
straight up to a noisy ~8.6x and straight back down the moment the
incident ends. The 1-hour long window rises more slowly during the
incident, keeps drifting for a while afterward (it's still averaging the
incident into its 60-minute lookback), and only drops back to baseline
once the incident has fully aged out of that window at minute 140 --
the "long window measures total burn, short window confirms it's
currently active" contrast the surrounding chapter text makes.
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

rng = np.random.default_rng(15)

T = np.arange(0, 180.001, 0.5)

INCIDENT_START = 60
INCIDENT_END = 80
LONG_WINDOW_CLEAR = 140  # incident fully ages out of the 1h long window
THRESHOLD = 14.4

# Short window (5 min): flat noisy baseline, noisy plateau during the
# incident, instant drop back to baseline the moment it ends.
SHORT = np.full_like(T, 0.32) + rng.normal(0, 0.05, T.size)
_incident_mask = (T >= INCIDENT_START) & (T <= INCIDENT_END)
SHORT[_incident_mask] = 8.6 + rng.normal(0, 0.55, _incident_mask.sum())
SHORT = np.clip(SHORT, 0.05, None)


def _long_window(t):
    """Smooth illustrative shape for the 1h long window: slow rise while
    the incident is entering the lookback, a plateau/slow decay while
    it's fully inside, then a sharp drop once it exits at minute 140."""
    y = np.full_like(t, 0.3)
    rise = (t >= INCIDENT_START) & (t <= INCIDENT_END)
    y[rise] = 0.3 + (3.5 - 0.3) * ((t[rise] - INCIDENT_START) / (INCIDENT_END - INCIDENT_START)) ** 0.75
    decay = (t > INCIDENT_END) & (t <= LONG_WINDOW_CLEAR)
    y[decay] = 1.0 + (3.5 - 1.0) * ((LONG_WINDOW_CLEAR - t[decay]) / (LONG_WINDOW_CLEAR - INCIDENT_END)) ** 1.15
    drop = (t > LONG_WINDOW_CLEAR) & (t <= LONG_WINDOW_CLEAR + 5)
    y[drop] = 1.0 - (1.0 - 0.3) * ((t[drop] - LONG_WINDOW_CLEAR) / 5)
    return y


LONG = _long_window(T)

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-burnrate.png (default locale, no suffix)
        "title": "Burn rate — kratak prozor (5 min) naspram dug prozor (1 h)",
        "xlabel": "minuti",
        "ylabel": "burn rate (×)",
        "short_label": "kratak prozor (potvrđuje trenutno trošenje)",
        "long_label": "dug prozor (meri ukupno trošenje)",
        "threshold_label": "prag brzog trošenja (14.4×)",
        "incident_label": "incident\n(20 min)",
        "annotation": (
            "alarm se gasi čim kratak\n"
            "prozor padne — ne čeka\n"
            "da dug prozor 'zaboravi'"
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-burnrate.en.png
        "title": "Burn rate — short window (5 min) vs. long window (1 h)",
        "xlabel": "minutes",
        "ylabel": "burn rate (×)",
        "short_label": "short window (confirms current burn)",
        "long_label": "long window (measures total burn)",
        "threshold_label": "fast-burn threshold (14.4×)",
        "incident_label": "incident\n(20 min)",
        "annotation": (
            "the alert clears as soon as the\n"
            "short window drops — it doesn't wait\n"
            "for the long window to 'forget'"
        ),
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
BLUE = "#2A78D6"
ORANGE = "#EB6834"
RED = "#E34948"
PINK_FILL = "#FCECEC"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(14.6, 5.75), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    ax.axvspan(INCIDENT_START, INCIDENT_END, facecolor=PINK_FILL, edgecolor="none", zorder=1)

    ax.plot(T, SHORT, color=BLUE, linewidth=1.6, label=cfg["short_label"], zorder=3)
    ax.plot(T, LONG, color=ORANGE, linewidth=2.4, label=cfg["long_label"], zorder=3)

    ax.axhline(THRESHOLD, color=RED, linestyle=(0, (4, 3)), linewidth=1.6, zorder=2)
    ax.text(
        183, THRESHOLD + 0.35, cfg["threshold_label"],
        fontsize=13, style="italic", color=RED, ha="right", va="bottom",
    )

    ax.text(
        62, 13.4, cfg["incident_label"],
        fontsize=13, style="italic", color=RED, ha="left", va="top",
    )

    ax.set_xlim(0, 180)
    ax.set_ylim(0, 19.5)

    ax.xaxis.set_major_locator(FixedLocator(range(0, 181, 20)))
    ax.yaxis.set_major_locator(FixedLocator(range(0, 17, 2)))

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

    legend = ax.legend(
        loc="upper left", frameon=False, fontsize=13.5,
        handlelength=1.8, bbox_to_anchor=(0.005, 0.99),
    )
    for text in legend.get_texts():
        text.set_color(INK)

    # Leader-line annotation pointing at where the short window drops back
    # to baseline while the long window is still elevated.
    ax.annotate(
        cfg["annotation"],
        xy=(83, 1.6),
        xytext=(93, 4.9),
        fontsize=12.5, style="italic", color=BLUE, va="bottom", ha="left",
        arrowprops=dict(arrowstyle="-", color=BLUE, linewidth=1.1,
                         connectionstyle="arc3,rad=-0.08"),
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-burnrate{cfg['suffix']}.png"
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
