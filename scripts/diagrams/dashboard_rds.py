#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-rds" chart used in
Poglavlje 7 / Chapter 7 (pull-obrasci / pull-patterns).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-rds.png was hand-built with no source file, so it could not be
re-rendered in English. This script reconstructs it from one parameterized
source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_rds.py sr   # -> docs/diagrams/dashboard-rds.png
    python3 scripts/diagrams/dashboard_rds.py en   # -> docs/diagrams/dashboard-rds.en.png
    python3 scripts/diagrams/dashboard_rds.py all  # both

Data note: illustrative two-layer, two-panel contrast for a managed RDS
instance over a 24-hour window.

Left panel — the *external* layer (CloudWatch): CPU% and replica lag on a
dual y-axis. Both show a sharp incident spike around hour ~14.5 (CPU jumps
from a ~15-20% baseline to ~43%, replica lag jumps from under a second to
~4.8s) — visible from *outside* the database even when it stops accepting
connections.

Right panel — the *internal* layer (postgres_exporter): sequential vs.
index scans per table over the same 24h, log-scale x-axis. Most tables are
healthy (index scans dominate); `audit_log` is the outlier — its sequential
scan count (red) dwarfs its index scan count (green), the textbook "missing
index" signature that only an internal-layer exporter can see.
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

rng = np.random.default_rng(7)

# ---- Left panel: CloudWatch-style CPU% + ReplicaLag(s) over 24h ----
HOURS = np.linspace(0, 24, 289)  # 5-minute resolution

SPIKE_CENTER = 14.6
SPIKE_WIDTH = 0.32
spike = 1.0 / (1.0 + ((HOURS - SPIKE_CENTER) / SPIKE_WIDTH) ** 2)  # Lorentzian bump

cpu_base = 22 + 6 * np.sin(2 * np.pi * (HOURS - 9) / 24) - 6 * np.exp(-((HOURS - 12) ** 2) / 18)
cpu_noise = rng.normal(0, 1.3, size=HOURS.size)
CPU = np.clip(cpu_base + cpu_noise + 28 * spike, 0, 60)

lag_base = 0.55 + 0.15 * np.sin(2 * np.pi * (HOURS - 6) / 24)
lag_noise = rng.normal(0, 0.06, size=HOURS.size)
REPLICA_LAG = np.clip(lag_base + lag_noise + 4.35 * spike, 0, 5)

# ---- Right panel: postgres_exporter seq vs. index scans (24h totals) ----
TABLES = ["orders", "sessions", "audit_log", "price_cache", "user_pref"]
INDEX_SCANS = [1_000_000, 280_000, 1_300, 150_000, 80_000]
SEQ_SCANS = [1_100, 320, 20_000, 220, 40]

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-rds.png (default locale, no suffix)
        "title_left": "CloudWatch (spoljašnja ravan) — CPU % i replika kašnjenje",
        "title_right": "postgres_exporter (unutrašnja ravan) — seq. vs indeks skenovi",
        "xlabel_left": "sati",
        "xlabel_right": "broj skenova (log skala, 24č)",
        "legend_cpu": "CPU %",
        "legend_lag": "ReplicaLag (s)",
        "legend_index": "indeks skenovi",
        "legend_seq": "sekvencijalni skenovi",
        "annotation_lag": "kašnjenje raste\n(spoljašnja ravan\nvidi ovo)",
        "annotation_audit": "audit_log: skoro\nsamo seq. skenovi\n— kandidat za indeks",
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-rds.en.png
        "title_left": "CloudWatch (external layer) — CPU % and replica lag",
        "title_right": "postgres_exporter (internal layer) — seq. vs index scans",
        "xlabel_left": "hours",
        "xlabel_right": "number of scans (log scale, 24h)",
        "legend_cpu": "CPU %",
        "legend_lag": "ReplicaLag (s)",
        "legend_index": "index scans",
        "legend_seq": "sequential scans",
        "annotation_lag": "lag rising\n(the external layer\nsees this)",
        "annotation_audit": "audit_log: almost\nonly seq. scans\n— index candidate",
    },
}

FIG_BG = "#F4F5F7"
AX_BG = "#FFFFFF"
GRID = "#E4E4E4"
INK = "#1F1F1F"
BLUE = "#2A78D6"
ORANGE = "#EB6834"
RED = "#E34948"
GREEN = "#1BAF7A"


def render(lang: str):
    cfg = LANGUAGES[lang]
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(14.6, 4.4), dpi=190)
    fig.patch.set_facecolor(FIG_BG)

    # ---------------- Left panel ----------------
    axL.set_facecolor(AX_BG)
    axL.fill_between(HOURS, CPU, color=BLUE, alpha=0.12, zorder=1)
    (l_cpu,) = axL.plot(HOURS, CPU, color=BLUE, linewidth=2.2, zorder=3, label=cfg["legend_cpu"])

    axL2 = axL.twinx()
    axL2.set_facecolor("none")
    (l_lag,) = axL2.plot(HOURS, REPLICA_LAG, color=ORANGE, linewidth=2.2,
                          linestyle="--", zorder=3, label=cfg["legend_lag"])

    axL.set_xlim(0, 24)
    axL.set_ylim(0, 60)
    axL2.set_ylim(0, 5)
    axL.xaxis.set_major_locator(FixedLocator([0, 5, 10, 15, 20]))

    axL.grid(True, which="major", axis="both", color=GRID, linewidth=1.0, zorder=0)
    axL.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        axL.spines[spine].set_visible(False)
    for spine in ("top", "left", "right"):
        axL2.spines[spine].set_visible(False)
    axL.spines["bottom"].set_color(INK)
    axL.spines["bottom"].set_linewidth(1.0)
    axL2.spines["right"].set_visible(True)
    axL2.spines["right"].set_color(INK)
    axL2.spines["right"].set_linewidth(1.0)

    axL.tick_params(axis="both", labelsize=12, colors=INK, length=0)
    axL2.tick_params(axis="y", labelsize=12, colors=INK, length=0)

    axL.set_xlabel(cfg["xlabel_left"], fontsize=13.5, color=INK, labelpad=10)
    axL.set_title(cfg["title_left"], fontsize=17, fontweight="bold", color=INK, loc="left", pad=14)

    axL.legend(handles=[l_cpu, l_lag], loc="upper left", frameon=False,
               fontsize=12.5, labelcolor=INK)

    axL.annotate(
        cfg["annotation_lag"],
        xy=(SPIKE_CENTER, 49), xytext=(SPIKE_CENTER + 0.6, 57),
        fontsize=11.5, style="italic", color=ORANGE, ha="left", va="top",
    )

    # ---------------- Right panel ----------------
    axR.set_facecolor(AX_BG)
    n = len(TABLES)
    y = np.arange(n)
    bar_h = 0.34

    axR.barh(y + bar_h / 2, INDEX_SCANS, height=bar_h, color=GREEN, zorder=3,
              label=cfg["legend_index"])
    axR.barh(y - bar_h / 2, SEQ_SCANS, height=bar_h, color=RED, zorder=3,
              label=cfg["legend_seq"])

    axR.set_xscale("log")
    axR.set_xlim(30, 2_000_000)
    axR.invert_yaxis()
    axR.set_yticks(y)
    axR.set_yticklabels(TABLES, fontsize=13.5)

    axR.grid(True, which="major", axis="x", color=GRID, linewidth=1.0, zorder=0)
    axR.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        axR.spines[spine].set_visible(False)
    axR.spines["bottom"].set_color(INK)
    axR.spines["bottom"].set_linewidth(1.0)

    axR.tick_params(axis="both", labelsize=12.5, colors=INK, length=0)

    axR.set_xlabel(cfg["xlabel_right"], fontsize=13.5, color=INK, labelpad=10)
    axR.set_title(cfg["title_right"], fontsize=17, fontweight="bold", color=INK, loc="left", pad=14)

    axR.legend(loc="lower right", frameon=False, fontsize=12.5, labelcolor=INK)

    audit_idx = TABLES.index("audit_log")
    axR.annotate(
        cfg["annotation_audit"],
        xy=(SEQ_SCANS[audit_idx], audit_idx - bar_h / 2),
        xytext=(35_000, audit_idx - 1.05),
        fontsize=11.5, style="italic", color=RED, ha="left", va="top",
    )

    fig.tight_layout()

    out_path = OUT_DIR / f"dashboard-rds{cfg['suffix']}.png"
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
