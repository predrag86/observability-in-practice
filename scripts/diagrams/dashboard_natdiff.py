#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-natdiff" chart used in
Poglavlje 22 / Chapter 22 (mreza-ravan-posmatranja / the network
observation plane).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-natdiff.png was hand-built with no source file, so it could not
be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_natdiff.py sr   # -> docs/diagrams/dashboard-natdiff.png
    python3 scripts/diagrams/dashboard_natdiff.py en   # -> docs/diagrams/dashboard-natdiff.en.png
    python3 scripts/diagrams/dashboard_natdiff.py all  # both

Data note: illustrative NAT/outbound-gateway byte counters over a 60-minute
window -- BytesInFromSource (inbound) and BytesOutToDestination (outbound),
the literal VPC flow-metric names referenced in the chapter text. The two
track each other closely outside the shaded 25-40 minute window; inside it,
BytesOutToDestination steadily falls away from BytesInFromSource (traffic
being lost somewhere in the gateway) and snaps back to normal the instant
the window ends -- the divergence-as-diagnostic point made in the
surrounding chapter text.
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

rng = np.random.default_rng(22)

MINUTES = np.linspace(0, 60, 360)
LOSS_START, LOSS_END = 25, 40
IN_REGION = (MINUTES >= LOSS_START) & (MINUTES <= LOSS_END)

BASELINE = 408.0

# BytesInFromSource: tracks baseline throughout, with only a mild dip-and-
# recover shape while the loss window is open (it is not loss-free -- the
# gateway itself is under strain -- but it never falls far).
IN_DIP = np.where(
    IN_REGION,
    35.0 * np.sin(np.pi * (MINUTES - LOSS_START) / (LOSS_END - LOSS_START)),
    0.0,
)
BYTES_IN = BASELINE - IN_DIP + rng.normal(0, 11, size=MINUTES.shape)

# BytesOutToDestination: tracks baseline outside the window, but inside it
# falls away steadily (traffic being lost) and snaps back to baseline the
# instant the window closes -- a hard edge at minute 40, not a smooth decay.
OUT_DROP = np.where(
    IN_REGION,
    183.0 * (MINUTES - LOSS_START) / (LOSS_END - LOSS_START),
    0.0,
)
BYTES_OUT = BASELINE - OUT_DROP + rng.normal(0, 11, size=MINUTES.shape)

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-natdiff.png (default locale, no suffix)
        "title": "Izlazni prolaz — bajtovi ulaz naspram izlaz, po minuti",
        "xlabel": "minuti",
        "ylabel": "bajtova/s (relativno)",
        "legend_in": "BytesInFromSource",
        "legend_out": "BytesOutToDestination",
        "annotation": (
            "razilaženje = gubitak\n"
            "(nijedan pojedinačan brojač\n"
            "ne bi ovo pokazao sam)"
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-natdiff.en.png
        "title": "Outbound gateway — bytes in vs out, per minute",
        "xlabel": "minutes",
        "ylabel": "bytes/s (relative)",
        "legend_in": "BytesInFromSource",
        "legend_out": "BytesOutToDestination",
        "annotation": (
            "divergence = loss\n"
            "(no single counter\n"
            "would show this on its own)"
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
    fig, ax = plt.subplots(figsize=(12.4, 4.9), dpi=190)
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)

    ax.axvspan(LOSS_START, LOSS_END, facecolor=PINK_FILL, edgecolor="none", zorder=1)

    ax.plot(MINUTES, BYTES_IN, color=BLUE, linewidth=1.8, label=cfg["legend_in"], zorder=3)
    ax.plot(MINUTES, BYTES_OUT, color=ORANGE, linewidth=1.8, label=cfg["legend_out"], zorder=3)

    ax.set_xlim(0, 60)
    ax.set_ylim(205, 448)
    ax.xaxis.set_major_locator(FixedLocator(range(0, 61, 10)))
    ax.yaxis.set_major_locator(FixedLocator([250, 300, 350, 400]))

    ax.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(INK)
    ax.spines["bottom"].set_color(INK)
    ax.spines["left"].set_linewidth(1.0)
    ax.spines["bottom"].set_linewidth(1.0)
    ax.tick_params(axis="both", labelsize=13, colors=INK, length=0)

    ax.set_xlabel(cfg["xlabel"], fontsize=14.5, color=INK, labelpad=10)
    ax.set_ylabel(cfg["ylabel"], fontsize=14.5, color=INK, labelpad=10)
    ax.set_title(cfg["title"], fontsize=19, fontweight="bold", color=INK, loc="left", pad=16)

    legend = ax.legend(
        loc="upper left", frameon=False, fontsize=13.5, labelcolor=INK,
        handlelength=1.8, borderaxespad=0.6,
    )

    ax.annotate(
        cfg["annotation"],
        xy=(33, 357),
        xytext=(41.5, 322),
        fontsize=13, style="italic", color=RED, va="top", ha="left",
        arrowprops=dict(arrowstyle="-", color=RED, linewidth=1.1, connectionstyle="arc3,rad=-0.15"),
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-natdiff{cfg['suffix']}.png"
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
