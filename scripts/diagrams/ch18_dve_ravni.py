#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch18-dve-ravni" diagram used in
Poglavlje 18 / Chapter 18 (baze-podataka / databases).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch18-dve-ravni.png was hand-built with no source file kept alongside it,
so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch18_dve_ravni.py sr   # -> docs/diagrams/ch18-dve-ravni.png
    python3 scripts/diagrams/ch18_dve_ravni.py en   # -> docs/diagrams/ch18-dve-ravni.en.png
    python3 scripts/diagrams/ch18_dve_ravni.py all  # both

Structure note: two independent collection layers sit side by side --
the external layer (the provider's own instance metrics, reached via
"virtualization metrics") and the internal layer (a dedicated exporter
reading the engine directly, reached via "TLS verify-full"). Both feed
the regular dashboard/alerts box, but only the internal layer also feeds
a dedicated meta-alert (hexagon) that watches whether the internal layer
itself is still producing fresh data -- if not, on-call gets paged, since
that gap can hide independently of whether the database itself is healthy.
"""

import sys
from pathlib import Path

from graphviz import Digraph

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "diagrams"

INK = "#5B4636"
BOX_FILL = "#EEEEEE"
BOX_LINE = "#999999"

LANGUAGES = {
    "sr": {
        "suffix": "",  # docs/diagrams/ch18-dve-ravni.png (default locale, no suffix)
        "nodes": {
            "engine": "Upravljana relaciona\nbaza\n(engine)",
            "external_box": "CPU · memorija · IOPS\nbroj konekcija · lag\nreplike",
            "internal_box": "Aktivne sesije · brave\nstatistika po\ntabeli/indeksu\ndugotrajni upiti",
            "dashboard": "Dashboard i alarmi",
            "meta_alert": "Poseban alarm:\nda li unutrašnja ravan\nuopšte diše?",
            "page": "Stranica dežurnom:\nmonitoring je pao,\nne nužno i baza",
        },
        "clusters": {
            "external": "Spoljna ravan — provajderove metrike instance",
            "internal": "Unutrašnja ravan — namenski exporter",
        },
        "edges": {
            "engine_external": "metrike virtuelizacije",
            "engine_internal": "TLS verify-full\ndirektno na instancu",
            "meta_alert_page": "nema svežih podataka",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch18-dve-ravni.en.png
        "nodes": {
            "engine": "Managed relational\ndatabase\n(engine)",
            "external_box": "CPU · memory · IOPS\nconnection count · lag\nreplicas",
            "internal_box": "Active sessions · locks\nper-table/index\nstatistics\nlong-running queries",
            "dashboard": "Dashboard and alerts",
            "meta_alert": "Dedicated alert:\nis the internal layer\nbreathing at all?",
            "page": "Page on-call:\nmonitoring is down,\nnot necessarily the database",
        },
        "clusters": {
            "external": "External layer — the provider's instance metrics",
            "internal": "Internal layer — a dedicated exporter",
        },
        "edges": {
            "engine_external": "virtualization metrics",
            "engine_internal": "TLS verify-full\ndirectly to the instance",
            "meta_alert_page": "no fresh data",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    c = cfg["clusters"]
    e = cfg["edges"]

    g = Digraph("ch18_dve_ravni", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.55", ranksep="0.65", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    g.node("engine", n["engine"], shape="cylinder")

    with g.subgraph(name="cluster_external") as ext:
        ext.attr(label=c["external"], style="rounded", color=BOX_LINE,
                 fontname="DejaVu Serif", labelloc="t")
        ext.node("external_box", n["external_box"])

    with g.subgraph(name="cluster_internal") as intl:
        intl.attr(label=c["internal"], style="rounded", color=BOX_LINE,
                  fontname="DejaVu Serif", labelloc="t")
        intl.node("internal_box", n["internal_box"])

    g.node("dashboard", n["dashboard"])
    g.node("meta_alert", n["meta_alert"], shape="hexagon", style="", fillcolor="")
    g.node("page", n["page"])

    g.edge("engine", "external_box", label=e["engine_external"])
    g.edge("engine", "internal_box", label=e["engine_internal"])

    g.edge("external_box", "dashboard")
    g.edge("internal_box", "dashboard")
    g.edge("internal_box", "meta_alert", style="dotted")

    g.edge("meta_alert", "page", label=e["meta_alert_page"])

    out_path = OUT_DIR / f"ch18-dve-ravni{cfg['suffix']}.png"
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
