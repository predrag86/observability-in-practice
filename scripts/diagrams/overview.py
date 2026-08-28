#!/usr/bin/env python3
"""
Source-of-truth generator for the "overview" system diagram used in the
Part II / Deo II introduction (deo-2-uvod / deo-2-uvod.en).

Why this file exists
---------------------
Same rationale as scripts/diagrams/cost_crossover.py: the original
overview.png was hand-built with no source file kept alongside it, so its
Serbian node/edge labels were baked into raster pixels with no way to
re-render them in English. This script reconstructs the diagram from one
parameterized Graphviz source, so both language variants come from the
same structure.

Usage
-----
    python3 scripts/diagrams/overview.py sr   # -> docs/diagrams/overview.png
    python3 scripts/diagrams/overview.py en   # -> docs/diagrams/overview.en.png
    python3 scripts/diagrams/overview.py all  # both

Structure note: this diagram shows the system the book's observability
setup *observes* -- application layer, auth, data layer, batch/ETL fleet,
network -- almost entirely on AWS, plus one independent SaaS exception.
Dotted arrows are the observing side (gateway, cloud platform); solid
arrows are regular application traffic. That distinction is structural,
not decorative -- every dotted arrow here gets its own chapter later in
Part II.
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
        "suffix": "",  # docs/diagrams/overview.png (default locale, no suffix)
        "nodes": {
            "browser": "Browser korisnika",
            "api_clients": "Eksterni API klijenti",
            "backend": "Backend servisi\n(Java + Python,\ndugotrajni)",
            "frontend_hosting": "Statički frontend\nhosting",
            "batch_etl": "Batch/ETL flota\n(ECS/Fargate, desetine\nporodica zadataka)",
            "auth": "Auth sloj\n(Keycloak-tipa identity\nprovider)",
            "managed_db": "Upravljane baze\n(RDS/Aurora-tipa)",
            "self_cluster": "Samostalno upravljan\ndistribuiran klaster\n(Dremio-tipa)",
            "gateway": "Gateway\n(Poglavlje 4)",
            "saas": "Nezavisan SaaS servis\n(Snowflake-tipa)\n— van AWS-a, van naše\nmreže",
            "cloud_platform": "Cloud observability\nplatforma\n(Poglavlje 3)",
        },
        "clusters": {
            "users": "Korisnici",
            "aws": "AWS — jedan nalog, jedan region",
            "app": "Sloj aplikacija",
            "data": "Sloj podataka",
            "observing": "Posmatračka strana (tema Dela II)",
        },
        "edges": {
            "browser_backend": "HTTPS",
            "api_backend": "HTTPS/REST",
            "backend_auth": "OIDC",
            "backend_db": "TLS",
            "backend_cluster": "upiti",
            "backend_gateway": "OTLP",
            "batch_cluster": "TLS",
            "batch_saas": "poziva",
            "batch_gateway": "OTLP, preko sidecar-a\n(Poglavlje 6)",
            "db_gateway": "pull, dve ravni\n(Poglavlje 7)",
            "cluster_gateway": "push, agent po čvoru\n(Poglavlje 7)",
            "saas_cloud": "pull, zakazano,\ndirektno (Poglavlje 7, 24)",
            "browser_cloud": "RUM, direktno\n(Poglavlje 8)",
        },
    },
    "en": {
        "suffix": ".en",  # docs/diagrams/overview.en.png
        "nodes": {
            "browser": "User's browser",
            "api_clients": "External API clients",
            "backend": "Backend services\n(Java + Python,\nlong-lived)",
            "frontend_hosting": "Static frontend\nhosting",
            "batch_etl": "Batch/ETL fleet\n(ECS/Fargate, dozens\nof job families)",
            "auth": "Auth layer\n(Keycloak-style identity\nprovider)",
            "managed_db": "Managed databases\n(RDS/Aurora-style)",
            "self_cluster": "Self-managed distributed\ncluster\n(Dremio-style)",
            "gateway": "Gateway\n(Chapter 4)",
            "saas": "Independent SaaS service\n(Snowflake-style)\n— outside AWS, outside\nour network",
            "cloud_platform": "Cloud observability\nplatform\n(Chapter 3)",
        },
        "clusters": {
            "users": "Users",
            "aws": "AWS — one account, one region",
            "app": "Application layer",
            "data": "Data layer",
            "observing": "Observing side (subject of Part II)",
        },
        "edges": {
            "browser_backend": "HTTPS",
            "api_backend": "HTTPS/REST",
            "backend_auth": "OIDC",
            "backend_db": "TLS",
            "backend_cluster": "queries",
            "backend_gateway": "OTLP",
            "batch_cluster": "TLS",
            "batch_saas": "calls",
            "batch_gateway": "OTLP, via sidecar\n(Chapter 6)",
            "db_gateway": "pull, two levels\n(Chapter 7)",
            "cluster_gateway": "push, agent per node\n(Chapter 7)",
            "saas_cloud": "pull, scheduled,\ndirect (Chapters 7, 24)",
            "browser_cloud": "RUM, direct\n(Chapter 8)",
        },
    },
}


def render(lang: str):
    cfg = LANGUAGES[lang]
    n = cfg["nodes"]
    c = cfg["clusters"]
    e = cfg["edges"]

    g = Digraph("overview", format="png")
    g.attr(bgcolor="white", fontname="DejaVu Serif", rankdir="TB",
           nodesep="0.55", ranksep="0.75", splines="spline")
    g.attr("node", fontname="DejaVu Serif", fontsize="14", margin="0.25,0.15",
           shape="box", style="filled", fillcolor=BOX_FILL, color=BOX_LINE)
    g.attr("edge", color=INK, fontname="DejaVu Serif", fontsize="12",
           arrowsize="0.7")

    # -- Users cluster --------------------------------------------------
    with g.subgraph(name="cluster_users") as u:
        u.attr(label=c["users"], style="rounded", color=BOX_LINE,
               fontname="DejaVu Serif", labelloc="t")
        u.node("browser", n["browser"])
        u.node("api_clients", n["api_clients"])

    # -- AWS cluster ------------------------------------------------------
    with g.subgraph(name="cluster_aws") as aws:
        aws.attr(label=c["aws"], style="rounded", color=BOX_LINE,
                 fontname="DejaVu Serif", labelloc="t")

        with aws.subgraph(name="cluster_app") as app:
            app.attr(label=c["app"], style="rounded", color=BOX_LINE,
                     fontname="DejaVu Serif", labelloc="t")
            app.node("backend", n["backend"])
            app.node("frontend_hosting", n["frontend_hosting"])

        aws.node("batch_etl", n["batch_etl"])
        aws.node("auth", n["auth"])

        with aws.subgraph(name="cluster_data") as data:
            data.attr(label=c["data"], style="rounded", color=BOX_LINE,
                      fontname="DejaVu Serif", labelloc="t")
            data.node("managed_db", n["managed_db"])
            data.node("self_cluster", n["self_cluster"])

        with aws.subgraph(name="cluster_observing") as obs:
            obs.attr(label=c["observing"], style="rounded", color=BOX_LINE,
                     fontname="DejaVu Serif", labelloc="t")
            obs.node("gateway", n["gateway"])

    # -- Outside AWS --------------------------------------------------
    g.node("saas", n["saas"])
    g.node("cloud_platform", n["cloud_platform"])

    # -- Regular traffic (solid) ----------------------------------------
    g.edge("browser", "backend", label=e["browser_backend"])
    g.edge("api_clients", "backend", label=e["api_backend"])
    g.edge("backend", "auth", label=e["backend_auth"])
    g.edge("backend", "managed_db", label=e["backend_db"])
    g.edge("backend", "self_cluster", label=e["backend_cluster"])
    g.edge("batch_etl", "self_cluster", label=e["batch_cluster"])
    g.edge("batch_etl", "saas", label=e["batch_saas"])
    g.edge("gateway", "cloud_platform")
    g.edge("browser", "cloud_platform", label=e["browser_cloud"])

    # -- Observing side (dashed/dotted, per the surrounding prose) -----
    g.edge("backend", "gateway", label=e["backend_gateway"], style="dotted")
    g.edge("batch_etl", "gateway", label=e["batch_gateway"], style="dotted")
    g.edge("managed_db", "gateway", label=e["db_gateway"], style="dotted")
    g.edge("self_cluster", "gateway", label=e["cluster_gateway"], style="dotted")
    g.edge("saas", "cloud_platform", label=e["saas_cloud"], style="dotted")

    out_path = OUT_DIR / f"overview{cfg['suffix']}.png"
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
