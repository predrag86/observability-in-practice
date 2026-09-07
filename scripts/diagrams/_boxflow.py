#!/usr/bin/env python3
"""
Shared renderer for the book's "stacked box flow" diagram style — the
plain, 2-3-box vertical-flow diagrams used for one-off chapter argument
diagrams (ch01-tri-uzroka.png, ch06-flush-prozor.png, ch25-rotacija-kljuca.png,
etc.). These are static PNGs with no original source script, so this module
lets us reproduce the same visual style for their English counterparts.

Usage from a per-chapter script:

    import sys
    sys.path.insert(0, "<dir containing this file>")
    from _boxflow import render_boxflow, Box

    render_boxflow(
        out_path,
        boxes=[
            Box(title="TITLE ONE", body="line one\nline two"),
            Box(title="TITLE TWO", body="line one\nline two", connector="short note text"),
        ],
    )

Box 1 has no connector (nothing above it). Each subsequent Box's
`connector` is the small note text rendered in the arrow between it and
the previous box (omit/None for a bare arrow). The connector's vertical
space scales with how many lines its note text has, so a long (3-4 line)
connector note doesn't overlap the boxes above/below it.
"""

from dataclasses import dataclass
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BOX_FILL = "#F4F6FB"
BOX_EDGE = "#7B86C4"
NOTE_FILL = "#EAECF6"
ARROW_COLOR = "#5C6BC0"
TEXT_COLOR = "#1A1A2E"
FONT = "DejaVu Sans"


@dataclass
class Box:
    title: str
    body: str
    connector: Optional[str] = None  # note text on the arrow ABOVE this box (None = box 1, or bare arrow)


def _connector_height(conn_text):
    """Vertical space to reserve for a gap, sized to fit the connector's
    note-box text (2 lines fits the historical fixed 0.75; each extra line
    adds room) — or the bare-arrow minimum when there's no note text."""
    if not conn_text:
        return 0.75
    n_lines = conn_text.count("\n") + 1
    return max(0.75, 0.42 + 0.34 * n_lines)


def render_boxflow(out_path, boxes, fig_width=8.4, box_width=8.0):
    n = len(boxes)
    # Rough vertical sizing: title + body lines determine box height.
    box_heights = []
    for b in boxes:
        n_body_lines = b.body.count("\n") + 1
        box_heights.append(1.0 + 0.42 * n_body_lines)

    # Per-gap connector height (index i = gap between box i-1 and box i).
    connector_heights = [_connector_height(b.connector) for b in boxes[1:]]

    total_h = sum(box_heights) + sum(connector_heights) + 0.6

    fig, ax = plt.subplots(figsize=(fig_width, total_h * 0.95))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, total_h)
    ax.axis("off")

    y = total_h - 0.3
    box_x = (10 - box_width) / 2
    prev_bottom = None
    for i, b in enumerate(boxes):
        h = box_heights[i]
        top = y
        bottom = top - h
        rect = FancyBboxPatch(
            (box_x, bottom), box_width, h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.6, edgecolor=BOX_EDGE, facecolor=BOX_FILL,
        )
        ax.add_patch(rect)
        ax.text(5, top - 0.32, b.title, ha="center", va="top",
                 fontsize=13, fontweight="bold", color=TEXT_COLOR, family=FONT)
        ax.text(5, bottom + (h - 0.5) / 2, b.body, ha="center", va="center",
                 fontsize=11.5, color=TEXT_COLOR, family=FONT, linespacing=1.6)

        incoming_gap_h = connector_heights[i - 1] if i > 0 else 0.75

        if prev_bottom is not None:
            gap_top = prev_bottom
            gap_bottom = top
            conn_text = boxes[i].connector
            if conn_text:
                note_h = incoming_gap_h * 0.8
                note_top = gap_top - (incoming_gap_h - note_h) / 2
                note_bottom = note_top - note_h
                note_w = box_width * 0.62
                note_x = (10 - note_w) / 2
                # short plain stub above the note (no arrowhead)
                ax.plot([5, 5], [gap_top, note_top], color=ARROW_COLOR, linewidth=1.8, solid_capstyle="butt")
                note_rect = FancyBboxPatch(
                    (note_x, note_bottom), note_w, note_h,
                    boxstyle="square,pad=0.0",
                    linewidth=0, facecolor=NOTE_FILL,
                )
                ax.add_patch(note_rect)
                ax.text(5, (note_top + note_bottom) / 2, conn_text, ha="center", va="center",
                         fontsize=10.5, color=TEXT_COLOR, family=FONT, linespacing=1.4)
                # arrowhead segment below the note, into the next box
                arrow = FancyArrowPatch(
                    (5, note_bottom), (5, gap_bottom),
                    arrowstyle="-|>", mutation_scale=14,
                    color=ARROW_COLOR, linewidth=1.8,
                )
                ax.add_patch(arrow)
            else:
                arrow = FancyArrowPatch(
                    (5, gap_top), (5, gap_bottom),
                    arrowstyle="-|>", mutation_scale=14,
                    color=ARROW_COLOR, linewidth=1.8,
                )
                ax.add_patch(arrow)

        prev_bottom = bottom
        outgoing_gap_h = connector_heights[i] if i < n - 1 else 0.0
        y = bottom - outgoing_gap_h

    fig.patch.set_facecolor("white")
    plt.tight_layout(pad=0.3)
    fig.savefig(out_path, dpi=160, facecolor="white")
    plt.close(fig)
    print(f"wrote {out_path}")
