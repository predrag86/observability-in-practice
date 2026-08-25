#!/usr/bin/env python3
"""
Source-of-truth generator for the "cost-crossover" chart used in
Poglavlje 3 / Chapter 3 (izbor-platforme / choosing-a-platform).

Why this file exists
---------------------
The original cost-crossover.png shipped in docs/diagrams/ was hand-built
(no vector/source file was kept alongside it). When the book started being
translated to English, that meant the chart's Serbian axis labels, series
names and annotation text were baked into raster pixels with no way to
re-render them in another language.

This script reconstructs the chart from a single parameterized source, so
that:
  - every language variant (docs/diagrams/cost-crossover.png for sr,
    cost-crossover.en.png for en, and any future locale) is generated from
    the SAME data and layout, not redrawn by hand each time;
  - if the underlying numbers ever need to change, they change once, here,
    and every language regenerates consistently;
  - adding a new language is just adding one entry to LANGUAGES below and
    re-running this script.

Usage
-----
    python3 scripts/diagrams/cost_crossover.py sr   # -> docs/diagrams/cost-crossover.png
    python3 scripts/diagrams/cost_crossover.py en   # -> docs/diagrams/cost-crossover.en.png
    python3 scripts/diagrams/cost_crossover.py all  # both

Data note: the underlying figures are the same illustrative/estimated
annual-cost figures used in the original chart (three fleet-size control
points: 100 / 500 / 2,000 hosts). They are not a new data source — this
script only changes how the numbers are rendered, not what they say.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import FixedLocator, FuncFormatter

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

# Illustrative / estimated annual cost, USD, at three fleet-size control
# points (100, 500, 2,000 hosts) -- same figures the original chart used.
X = [100, 500, 2000]

SERIES = {
    "grafana_cloud": {
        "y": [17000, 90000, 210000],
        "band": 0.22,
        "color": "#2E63C7",
        "marker": "o",
        "linestyle": "-",
        "mfc": "white",
    },
    "self_hosted": {
        "y": [42000, 135000, 800000],
        "band": 0.20,
        "color": "#1E9E77",
        "marker": "^",
        "linestyle": ":",
        "mfc": "white",
    },
    "datadog": {
        "y": [55000, 310000, 950000],
        "band": 0.18,
        "color": "#E2622B",
        "marker": "s",
        "linestyle": "--",
        "mfc": "white",
    },
}

YTICKS = [15000, 30000, 60000, 125000, 250000, 500000, 1100000]

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/cost-crossover.png (default locale, no suffix)
        "xlabel": "Veličina flote (broj hostova)",
        "ylabel": "Procenjen godišnji trošak (USD, log skala)",
        "series_labels": {
            "grafana_cloud": "Grafana Cloud",
            "self_hosted": "Self-hosted OSS",
            "datadog": "Datadog",
        },
        "xtick_fmt": lambda v: f"{v:,.0f}".replace(",", "."),
        "ytick_fmt": lambda v: (
            f"${v/1_000_000:.1f}M" if v >= 1_000_000 else f"${v/1000:.0f}k"
        ),
        "annotation": (
            "Self-hosted OSS retko postaje jeftiniji od\n"
            "Grafana Cloud commit cene pre ~2.000 hostova\n"
            "— i tek uz poseban razlog (compliance, rezidencija podataka)."
        ),
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/cost-crossover.en.png
        "xlabel": "Fleet size (number of hosts)",
        "ylabel": "Estimated annual cost (USD, log scale)",
        "series_labels": {
            "grafana_cloud": "Grafana Cloud",
            "self_hosted": "Self-hosted OSS",
            "datadog": "Datadog",
        },
        "xtick_fmt": lambda v: f"{v:,.0f}",
        "ytick_fmt": lambda v: (
            f"${v/1_000_000:.1f}M" if v >= 1_000_000 else f"${v/1000:.0f}k"
        ),
        "annotation": (
            "Self-hosted OSS rarely gets cheaper than\n"
            "Grafana Cloud's commit pricing before ~2,000 hosts\n"
            "— and only for a specific reason (compliance, data residency)."
        ),
    },
}

BG = "#FAF8F4"
INK = "#2B2118"
GRID = "#DDD7CC"

SERIF = None
for candidate in ("Georgia", "DejaVu Serif", "Liberation Serif", "serif"):
    try:
        fm.findfont(candidate, fallback_to_default=False)
        SERIF = candidate
        break
    except Exception:
        continue
SERIF = SERIF or "serif"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, ax = plt.subplots(figsize=(11, 7), dpi=180)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    for key, s in SERIES.items():
        y = s["y"]
        lower = [v * (1 - s["band"]) for v in y]
        upper = [v * (1 + s["band"]) for v in y]
        ax.fill_between(X, lower, upper, color=s["color"], alpha=0.12, zorder=1)
        ax.plot(
            X, y,
            color=s["color"], linestyle=s["linestyle"], linewidth=2.4,
            marker=s["marker"], markersize=11, markerfacecolor=s["mfc"],
            markeredgecolor=s["color"], markeredgewidth=2.2,
            zorder=3,
        )
        # error caps at each point
        for xi, yi, lo, hi in zip(X, y, lower, upper):
            ax.plot([xi, xi], [lo, hi], color=s["color"], linewidth=1.2, alpha=0.5, zorder=2)

        label = cfg["series_labels"][key]
        label_dy = {"datadog": 10, "self_hosted": -22, "grafana_cloud": 0}[key]
        ax.annotate(
            label,
            xy=(X[-1], y[-1]),
            xytext=(14, label_dy),
            textcoords="offset points",
            fontsize=15, fontweight="bold", color=s["color"],
            fontfamily=SERIF, va="center",
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(85, 3200)
    ax.set_ylim(11000, 1500000)

    ax.xaxis.set_major_locator(FixedLocator(X))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: cfg["xtick_fmt"](v)))
    ax.xaxis.set_minor_locator(FixedLocator([]))

    ax.yaxis.set_major_locator(FixedLocator(YTICKS))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: cfg["ytick_fmt"](v)))
    ax.yaxis.set_minor_locator(FixedLocator([]))

    ax.tick_params(axis="both", labelsize=13, colors=INK, length=0)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily(SERIF)

    ax.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    for spine_name in ("top", "right", "left"):
        ax.spines[spine_name].set_visible(False)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(1.2)

    ax.set_xlabel(cfg["xlabel"], fontsize=15, color=INK, fontfamily=SERIF, labelpad=14)
    ax.set_ylabel(cfg["ylabel"], fontsize=15, color=INK, fontfamily=SERIF, labelpad=14)

    # Annotation pointing at the Datadog/Self-hosted crossover near 2,000 hosts
    ax.annotate(
        cfg["annotation"],
        xy=(1750, SERIES["self_hosted"]["y"][-1] * 0.92),
        xytext=(430, SERIES["datadog"]["y"][-1] * 1.55),
        fontsize=13.5, style="italic", color="#5B4636", fontfamily=SERIF,
        arrowprops=dict(arrowstyle="-", color="#A99C86", linewidth=1.1,
                         connectionstyle="arc3,rad=0.15"),
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"cost-crossover{cfg['suffix']}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=BG, bbox_inches="tight")
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
