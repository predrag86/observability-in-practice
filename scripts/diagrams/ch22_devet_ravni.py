#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch22-devet-ravni" diagram used in
Poglavlje 22 / Chapter 22 (mreza-ravan-posmatranja / network-as-an-
observation-plane).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch22-devet-ravni.png was hand-built with no source file kept alongside
it, so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch22_devet_ravni.py sr   # -> docs/diagrams/ch22-devet-ravni.png
    python3 scripts/diagrams/ch22_devet_ravni.py en   # -> docs/diagrams/ch22-devet-ravni.en.png
    python3 scripts/diagrams/ch22_devet_ravni.py all  # both

Structure note: nine independent network observation planes (the chapter
text names nine; the diagram groups "edge" and "abuse protection" into
one box, so eight boxes total), grouped into four visibility categories
stacked top to bottom by how well each plane self-reports its own
failure: live metrics (best) / log-only / blind-no-telemetry / blind AND
carries everyone else's telemetry (worst, tan cluster -- the same
note/summary tan used elsewhere in the book). Two independent structural
edges leave the grouping: the outbound gateway (NAT) feeds a differential-
reading check (hexagon) that concludes in a "divergence = diagnosis" box,
and the worst-group cluster has a dotted edge to a dashed warning box,
since that whole grouping's relationship to failure is inferential, not a
direct data edge.
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"
NOTE_FILL = "#F4EFE6"
NOTE_LINE = "#8B7355"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch22-devet-ravni.png (default locale, no suffix)
        "nodes": {
            "edge_abuse": "Rub / zaštita od\nzloupotrebe",
            "traffic_balance": "Balansiranje saobraćaja",
            "nat": "Izlazni prolaz (NAT)",
            "private_links": "Privatne veze ka\nservisima",
            "iface": "Mrežni interfejs\ninstance",
            "dns": "DNS razrešavanje",
            "metadata": "Servis metapodataka",
            "clock": "Sinhronizacija sata",
            "diff_read": "Diferencijalno čitanje:\nulaz naspram izlaza\nu paru, ne pojedinačno",
            "divergence": "Razilaženje =\ndijagnostika\n(gubitak, ne samo\n'nema alarma')",
            "warning": "Kad ova ravan padne,\nmože ugasiti signal\nsvih ostalih ravni",
        },
        "clusters": {
            "live": "Metrika uživo",
            "log": "Samo log",
            "blind": "Slepo — bez direktne telemetrije",
            "blind_path": "Slepo I put telemetrije — najgora grupa",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch22-devet-ravni.en.png
        "nodes": {
            "edge_abuse": "Edge / abuse\nprotection",
            "traffic_balance": "Traffic balancing",
            "nat": "Outbound gateway (NAT)",
            "private_links": "Private links to\nservices",
            "iface": "Instance network\ninterface",
            "dns": "DNS resolution",
            "metadata": "Metadata service",
            "clock": "Clock sync",
            "diff_read": "Differential reading:\ninbound vs. outbound,\nas a pair, not individually",
            "divergence": "Divergence =\ndiagnosis\n(loss, not just\n'no alert')",
            "warning": "When this plane goes down,\nit can kill the signal\nof all the other planes",
        },
        "clusters": {
            "live": "Live metrics",
            "log": "Log only",
            "blind": "Blind — no direct telemetry",
            "blind_path": "Blind AND the telemetry path — worst group",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    c = cfg["clusters"]

    g = Digraph("ch22_devet_ravni", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.45", ranksep="0.55", splines="spline",
           margin="0.3,0.3")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    with g.subgraph(name="cluster_live") as live:
        live.attr(label=c["live"], style="rounded", color=BOX_LINE,
                  fontname="DejaVu Serif", labelloc="t")
        live.node("edge_abuse", n["edge_abuse"])
        live.node("traffic_balance", n["traffic_balance"])

    with g.subgraph(name="cluster_log") as log:
        log.attr(label=c["log"], style="rounded", color=BOX_LINE,
                 fontname="DejaVu Serif", labelloc="t")
        log.node("nat", n["nat"])
        log.node("private_links", n["private_links"])

    with g.subgraph(name="cluster_blind") as blind:
        blind.attr(label=c["blind"], style="rounded", color=BOX_LINE,
                   fontname="DejaVu Serif", labelloc="t")
        blind.node("iface", n["iface"])

    with g.subgraph(name="cluster_blind_path") as bp:
        bp.attr(label=c["blind_path"], style="filled,rounded",
                fillcolor=NOTE_FILL, color=NOTE_LINE,
                fontname="DejaVu Serif", labelloc="t")
        bp.node("dns", n["dns"])
        bp.node("metadata", n["metadata"])
        bp.node("clock", n["clock"])

    g.node("diff_read", n["diff_read"], shape="hexagon", fillcolor=NOTE_FILL,
           color=NOTE_LINE)
    g.node("divergence", n["divergence"])
    g.node("warning", n["warning"], style="dashed,filled", fillcolor="white",
           color=INK)

    # Invisible ordering edges: force the four grouping clusters to stack
    # top to bottom in the same "best-to-worst visibility" order as the
    # original, since the groupings themselves have no real edges between
    # them.
    g.edge("edge_abuse", "nat", style="invis")
    g.edge("nat", "iface", style="invis")
    g.edge("iface", "dns", style="invis")

    # Real structural edges.
    g.edge("nat", "diff_read")
    g.edge("diff_read", "divergence")
    g.edge("metadata", "warning", style="dotted")

    out_path = OUT_DIR / f"ch22-devet-ravni{cfg['suffix']}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g.render(outfile=str(out_path), cleanup=True)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    targets = sys.argv[1:] or ["en"]
    if targets == ["all"]:
        targets = list(LANGUAGES.keys())
    for t in targets:
        if t not in LANGUAGES:
            raise SystemExit(f"unknown language {t!r}, known: {list(LANGUAGES)}")
        render(t)
