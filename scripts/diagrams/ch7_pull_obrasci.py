#!/usr/bin/env python3
"""
Source-of-truth generator for the "ch7-pull-obrasci" diagram used in
Poglavlje 7 / Chapter 7 (pull-obrasci / pull-based patterns).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
ch7-pull-obrasci.png was hand-built with no source file kept alongside
it, so its Serbian labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/ch7_pull_obrasci.py sr   # -> docs/diagrams/ch7-pull-obrasci.png
    python3 scripts/diagrams/ch7_pull_obrasci.py en   # -> docs/diagrams/ch7-pull-obrasci.en.png
    python3 scripts/diagrams/ch7_pull_obrasci.py all  # both

Structure note: three independent pull-based patterns, side by side, by
level of control -- a managed database (two independent scrape layers,
external + internal), a self-managed cluster (an agent that pushes,
rather than being scraped), and an external SaaS (a scheduled pull that
bypasses the gateway entirely). The "extraction from the source" edges
(database -> its two scrapers; SaaS views -> scheduled Lambda) are drawn
dotted, matching the observing-side convention from overview.py; the
"delivery to the gateway/platform" edges are solid.
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
        "suffix": "",  # docs/diagrams/ch7-pull-obrasci.png (default locale, no suffix)
        "nodes": {
            "db": "Baza",
            "cloudwatch": "CloudWatch\n(spoljašnja ravan)",
            "pg_exporter": "postgres_exporter\n(unutrašnja ravan, read-\nonly)",
            "node1": "Čvor 1",
            "node2": "Čvor 2",
            "node3": "Čvor N",
            "alloy": "Alloy agent\npo čvoru",
            "saas_views": "Account-usage pogledi",
            "lambda": "Zakazana Lambda",
            "gateway": "Gateway\n(Poglavlje 4)",
            "cloud_platform": "Cloud platforma",
        },
        "clusters": {
            "db": "Upravljana baza (RDS/Aurora-tipa)",
            "cluster": "Samostalno upravljan klaster (Dremio-tipa)",
            "saas": "SaaS bez agenta (Snowflake-tipa)",
        },
        "edges": {
            "cloudwatch_gateway": "pull, bez kredencijala\nbaze",
            "pg_exporter_gateway": "pull, TLS, read-only rola",
            "alloy_gateway": "push, bez cloud\nkredencijala",
            "lambda_platform": "pull, zakazano,\ndirektno, zaobilazi\ngateway",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/ch7-pull-obrasci.en.png
        "nodes": {
            "db": "Database",
            "cloudwatch": "CloudWatch\n(external layer)",
            "pg_exporter": "postgres_exporter\n(internal layer, read-\nonly)",
            "node1": "Node 1",
            "node2": "Node 2",
            "node3": "Node N",
            "alloy": "Alloy agent\nper node",
            "saas_views": "Account-usage views",
            "lambda": "Scheduled Lambda",
            "gateway": "Gateway\n(Chapter 4)",
            "cloud_platform": "Cloud platform",
        },
        "clusters": {
            "db": "Managed database (RDS/Aurora-style)",
            "cluster": "Self-managed cluster (Dremio-style)",
            "saas": "Agentless SaaS (Snowflake-style)",
        },
        "edges": {
            "cloudwatch_gateway": "pull, no database\ncredentials",
            "pg_exporter_gateway": "pull, TLS, read-only role",
            "alloy_gateway": "push, no cloud\ncredentials",
            "lambda_platform": "pull, scheduled,\ndirect, bypasses\ngateway",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    c = cfg["clusters"]
    e = cfg["edges"]

    g = Digraph("ch7_pull_obrasci", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.5", ranksep="0.55", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    # -- Managed database cluster ---------------------------------------
    with g.subgraph(name="cluster_db") as d:
        d.attr(label=c["db"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        d.node("db", n["db"])

    # -- Self-managed cluster ---------------------------------------------
    with g.subgraph(name="cluster_cluster") as k:
        k.attr(label=c["cluster"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        k.node("node1", n["node1"])
        k.node("node2", n["node2"])
        k.node("node3", n["node3"])

    # -- Agentless SaaS -----------------------------------------------
    with g.subgraph(name="cluster_saas") as s:
        s.attr(label=c["saas"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        s.node("saas_views", n["saas_views"])

    g.node("cloudwatch", n["cloudwatch"])
    g.node("pg_exporter", n["pg_exporter"])
    g.node("alloy", n["alloy"])
    g.node("lambda", n["lambda"])
    g.node("gateway", n["gateway"])
    g.node("cloud_platform", n["cloud_platform"])

    # -- Extraction from the source (dotted, observing side) -----------
    g.edge("db", "cloudwatch", style="dotted")
    g.edge("db", "pg_exporter", style="dotted")
    g.edge("saas_views", "lambda", style="dotted")

    # -- Node agent (solid: it actively pushes, not scraped) -----------
    g.edge("node1", "alloy")
    g.edge("node2", "alloy")
    g.edge("node3", "alloy")

    # -- Delivery to the gateway / platform (solid) ---------------------
    g.edge("cloudwatch", "gateway", label=e["cloudwatch_gateway"])
    g.edge("pg_exporter", "gateway", label=e["pg_exporter_gateway"])
    g.edge("alloy", "gateway", label=e["alloy_gateway"])
    g.edge("lambda", "cloud_platform", label=e["lambda_platform"])

    out_path = OUT_DIR / f"ch7-pull-obrasci{cfg['suffix']}.png"
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
