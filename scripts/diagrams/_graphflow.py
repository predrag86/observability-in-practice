#!/usr/bin/env python3
"""
Shared drawing primitives for the book's more complex hand-authored
diagrams (containers, converging/diverging arrows, cylinders) — same
visual palette as _boxflow.py (light blue-gray boxes, blue border,
indigo arrows), but free-form coordinates instead of a fixed vertical
stack, for diagrams with branching, converging or nested-container
layouts (ch18/19/20/21/22/23/24 "mehanizam"/"faze"/"kolektor"-style
diagrams).

All coordinates are in axes data-space set up by `new_figure(w, h)`,
origin bottom-left, matching typical page layout (x grows right, y
grows up).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Ellipse
from matplotlib.path import Path as MplPath
import numpy as np

BOX_FILL = "#F4F6FB"
BOX_EDGE = "#7B86C4"
CONTAINER_FILL = "#FAFBFE"
CONTAINER_EDGE = "#C7CCE8"
NOTE_FILL = "#EAECF6"
ARROW_COLOR = "#5C6BC0"
TEXT_COLOR = "#1A1A2E"
FONT = "DejaVu Sans"


def new_figure(w, h, dpi=160):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.set_aspect("equal")
    return fig, ax


def container(ax, x, y, w, h):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.3, edgecolor=CONTAINER_EDGE, facecolor=CONTAINER_FILL, zorder=0,
    )
    ax.add_patch(rect)


def box(ax, x, y, w, h, text, fontsize=10.5, bold_lines=0, fill=None, edge=None):
    """Box with bottom-left corner at (x, y). `bold_lines` = number of
    leading lines (from the top) to render bold (0 = none, i.e. all plain)."""
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        linewidth=1.4, edgecolor=edge or BOX_EDGE, facecolor=fill or BOX_FILL, zorder=2,
    )
    ax.add_patch(rect)
    lines = text.split("\n")
    if bold_lines:
        bold_part = "\n".join(lines[:bold_lines])
        rest = "\n".join(lines[bold_lines:])
        cy = y + h / 2
        if rest:
            ax.text(x + w / 2, cy - 0.06 * h, bold_part, ha="center", va="bottom",
                     fontsize=fontsize, fontweight="bold", color=TEXT_COLOR, family=FONT, zorder=3)
            ax.text(x + w / 2, cy - 0.10 * h, rest, ha="center", va="top",
                     fontsize=fontsize, color=TEXT_COLOR, family=FONT, linespacing=1.5, zorder=3)
        else:
            ax.text(x + w / 2, cy, bold_part, ha="center", va="center",
                     fontsize=fontsize, fontweight="bold", color=TEXT_COLOR, family=FONT, zorder=3)
    else:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                 fontsize=fontsize, color=TEXT_COLOR, family=FONT, linespacing=1.5, zorder=3)


def cylinder(ax, x, y, w, h, text, fontsize=10):
    """Simple flat-sided cylinder (database) shape, bottom-left at (x, y)."""
    ell_h = h * 0.18
    body = Rectangle((x, y + ell_h / 2), w, h - ell_h, linewidth=1.4,
                      edgecolor=BOX_EDGE, facecolor=BOX_FILL, zorder=2)
    ax.add_patch(body)
    bottom = Ellipse((x + w / 2, y + ell_h / 2), w, ell_h, linewidth=1.4,
                      edgecolor=BOX_EDGE, facecolor=BOX_FILL, zorder=1)
    ax.add_patch(bottom)
    top = Ellipse((x + w / 2, y + h - ell_h / 2), w, ell_h, linewidth=1.4,
                   edgecolor=BOX_EDGE, facecolor=BOX_FILL, zorder=3)
    ax.add_patch(top)
    ax.text(x + w / 2, y + h / 2 - ell_h * 0.3, text, ha="center", va="center",
             fontsize=fontsize, color=TEXT_COLOR, family=FONT, linespacing=1.4, zorder=4)


def arrow(ax, p1, p2, label=None, dotted=False, curved=0.0, label_dx=0.0, label_dy=0.0,
          fontsize=9.5, lw=1.6):
    style = "-|>"
    connectionstyle = f"arc3,rad={curved}" if curved else None
    a = FancyArrowPatch(
        p1, p2, arrowstyle=style, mutation_scale=13,
        color=ARROW_COLOR, linewidth=lw,
        linestyle=(0, (2, 2)) if dotted else "solid",
        connectionstyle=connectionstyle, zorder=1.5,
    )
    ax.add_patch(a)
    if label:
        mx = (p1[0] + p2[0]) / 2 + label_dx
        my = (p1[1] + p2[1]) / 2 + label_dy
        ax.text(mx, my, label, ha="center", va="center", fontsize=fontsize,
                 color=TEXT_COLOR, family=FONT, linespacing=1.3, zorder=4,
                 bbox=dict(boxstyle="square,pad=0.15", facecolor=NOTE_FILL, edgecolor="none"))


def save(fig, out_path):
    fig.patch.set_facecolor("white")
    plt.tight_layout(pad=0.3)
    fig.savefig(out_path, dpi=160, facecolor="white")
    plt.close(fig)
    print(f"wrote {out_path}")
