#!/usr/bin/env python3
"""
Source-of-truth generator for the "dashboard-pseudonymization" chart used in
Poglavlje 25 / Chapter 25 (privatnost-telemetriji / privacy-in-telemetry).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
dashboard-pseudonymization.png was hand-built with no source file, so it
could not be re-rendered in English. This script reconstructs it from one
parameterized source so both language variants come from the same data.

Usage
-----
    python3 scripts/diagrams/dashboard_pseudonymization.py sr   # -> docs/diagrams/dashboard-pseudonymization.png
    python3 scripts/diagrams/dashboard_pseudonymization.py en   # -> docs/diagrams/dashboard-pseudonymization.en.png
    python3 scripts/diagrams/dashboard_pseudonymization.py all  # both

Data note: illustrative debugging-panel mockup, not a real chart. Two
before/after panels reproduce the same two trace/session pairs: BEFORE, the
front-end field (user.id) and back-end field (enduser.id) each write a raw
identifier (a UUID fragment on the front, a real email on the back) that
trivially re-identifies the person once joined by trace. AFTER, both ends
write the same derived (keyed-hash) pseudonym, so trace-based joining still
works for debugging but no longer reveals the real identity.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

# Two trace/session pairs, each with a front-end row and a back-end row.
# "before" email domains are localized per language (see LANGUAGES), so they
# are left as a format placeholder here and filled in per-render.
ROWS = [
    {"trace": "aK9mZq2Ltp", "field": "user.id (front)",
     "before": "9f3c2e11-...", "after": "u_7f2a19c04b8e"},
    {"trace": "aK9mZq2Ltp", "field": "enduser.id (back)",
     "before": "j.smith@{domain}", "after": "u_7f2a19c04b8e"},
    {"trace": "hR7wNv5Xbq", "field": "user.id (front)",
     "before": "1a7bd902-...", "after": "u_3d81e0f4a2c1"},
    {"trace": "hR7wNv5Xbq", "field": "enduser.id (back)",
     "before": "m.doe@{domain}", "after": "u_3d81e0f4a2c1"},
]

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/dashboard-pseudonymization.png (default locale, no suffix)
        "title_before": "PRE — deljen kontekst trejsa\notkriva identitet",
        "title_after": "POSLE — oba kraja pišu isti\noblik pseudonima",
        "col_trace": "trace/session",
        "col_field": "polje",
        "col_value": "vrednost",
        "same_person": "ista\nosoba",
        "email_domain": "primer-firma.com",
        "footer_before": "svaki par se lako spaja preko trace-context-a\nu pravo ime i email",
        "footer_after": "spajanje i dalje radi za otklanjanje grešaka,\nali ne otkriva identitet",
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/dashboard-pseudonymization.en.png
        "title_before": "BEFORE — shared trace context\nreveals identity",
        "title_after": "AFTER — both ends write the\nsame pseudonym form",
        "col_trace": "trace/session",
        "col_field": "field",
        "col_value": "value",
        "same_person": "same\nperson",
        "email_domain": "example-corp.com",
        "footer_before": "each pair is trivially joined via trace context\nback to a real name and email",
        "footer_after": "joining still works for debugging, but no\nlonger reveals identity",
    },
}

FIG_BG = "#F4F5F7"
INK = "#1F1F1F"
GRAY = "#7A7A7A"
RED = "#E34948"
GREEN = "#1BAF7A"

ROW_Y = [0.74, 0.62, 0.40, 0.28]
COL_X = {"trace": 0.0, "field": 0.27, "value": 0.51}


def _panel(ax, cfg, title, value_key, color, footer_key):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(FIG_BG)

    ax.text(0.0, 0.97, title, fontsize=15, fontweight="bold", color=INK,
             ha="left", va="top", linespacing=1.3, clip_on=True)

    ax.text(COL_X["trace"], 0.80, cfg["col_trace"], fontsize=11.5,
             fontweight="bold", color=GRAY, ha="left", va="bottom", clip_on=True)
    ax.text(COL_X["field"], 0.80, cfg["col_field"], fontsize=11.5,
             fontweight="bold", color=GRAY, ha="left", va="bottom", clip_on=True)
    ax.text(COL_X["value"], 0.80, cfg["col_value"], fontsize=11.5,
             fontweight="bold", color=GRAY, ha="left", va="bottom", clip_on=True)

    for row, y in zip(ROWS, ROW_Y):
        value = row[value_key].format(domain=cfg["email_domain"])
        ax.text(COL_X["trace"], y, row["trace"], fontsize=12, color=INK,
                 ha="left", va="center", clip_on=True)
        ax.text(COL_X["field"], y, row["field"], fontsize=12, color=INK,
                 ha="left", va="center", clip_on=True)
        ax.text(COL_X["value"], y, value, fontsize=10.5, fontweight="bold",
                 color=color, ha="left", va="center", clip_on=True)

    # brackets + "same person" labels, one per trace pair
    bracket_x = 0.87
    for y_top, y_bot in [(ROW_Y[0], ROW_Y[1]), (ROW_Y[2], ROW_Y[3])]:
        ax.plot([bracket_x, bracket_x], [y_top + 0.05, y_bot - 0.05],
                 color=color, linewidth=1.5, alpha=0.6, zorder=2, clip_on=True)
        ax.text(bracket_x + 0.02, (y_top + y_bot) / 2, cfg["same_person"],
                 fontsize=9, color=color, ha="left", va="center", clip_on=True)

    ax.text(0.0, 0.13, cfg[footer_key], fontsize=11.5, style="italic",
             color=color, ha="left", va="top", linespacing=1.4, clip_on=True)


def render(lang: str):
    cfg = LANGUAGES[lang]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(15.6, 5.7), dpi=190,
        gridspec_kw={"wspace": 0.30, "left": 0.015, "right": 0.985,
                     "top": 0.97, "bottom": 0.03},
    )
    fig.patch.set_facecolor(FIG_BG)

    _panel(ax1, cfg, cfg["title_before"], "before", RED, "footer_before")
    _panel(ax2, cfg, cfg["title_after"], "after", GREEN, "footer_after")

    out_path = OUT_DIR / f"dashboard-pseudonymization{cfg['suffix']}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=FIG_BG)
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
