---
hide:
  - navigation
  - toc
---

<!-- Homepage hero: a raw HTML section with the H1 nested inside it,
     for the full-bleed background image treatment. -->
<!-- markdownlint-disable MD033 MD041 -->

<div class="hero" markdown="1">
<div class="hero-content" markdown="1">

# Observability in Practice

OpenTelemetry and the Grafana LGTM stack
{: .hero-tagline }

</div>
</div>

<!-- markdownlint-enable MD033 MD041 -->

A book structured around the real, multi-month evolution of a production
observability system implemented company-wide — a portfolio spanning dozens
of backend and frontend applications, network infrastructure, managed and
self-managed databases, distributed compute clusters, an authentication
layer, and a fleet of batch/ETL jobs, all on AWS, plus one independent SaaS
service sitting outside that infrastructure.

Every chapter combines theory (why it's done this way) with concrete,
anonymized examples from the implementation: real PromQL/LogQL queries, real
mistakes that were made, and the real reasoning behind what was rejected.

!!! note "Anonymization"
    All company names, people's names, internal domains, resource IDs, and
    other identifying details have been intentionally removed or
    generalized — the book relies on **patterns and decisions**, not on
    whose they were.

## Who this is for

DevOps/SRE engineers, backend developers instrumenting their own service, and
team leads who need to decide self-hosted vs. Grafana Cloud and justify the
cost.

The book assumes basic working knowledge of DevOps/SRE practice (Linux,
containers, CI/CD, cloud infrastructure) and an introductory understanding of
observability concepts (metrics, logs, traces). Prior experience with
OpenTelemetry isn't necessary — it's explained starting in Chapter 2.

## Structure

| Part | Topic |
| --- | --- |
| [Introduction](uvod.en.md) | Why this book, and how it's different |
| [Part I](poglavlje-01-sta-je-observability.en.md) | Fundamentals — what observability is, OpenTelemetry, choosing a platform |
| [Part II](deo-2-uvod.md) | Telemetry-collection architecture — gateway, instrumentation, sidecar |
| [Part III](poglavlje-10-anatomija-pipeline.md) | Processing, cardinality, and cost |
| [Part IV](poglavlje-13-arhitektura-alarmiranja.md) | Alerting, SLOs, and incident response |
| [Part V](poglavlje-18-baze-podataka.md) | Observability by domain — databases, clusters, network, batch/ETL, Snowflake |
| [Part VI](poglavlje-25-privatnost-telemetriji.md) | Governance, compliance, and maturity |
| [Part VII](poglavlje-29-fazni-rollout.md) | Maturing the program |
| [Appendices](dodatak-a-promql-logql-recepti.md) | PromQL/LogQL recipes, glossary, onboarding checklist, templates |

Every standard chapter follows the same shape: an opening analogy from
everyday life, a practical section (how it was actually done, with an
architecture diagram and, where relevant, an illustrative dashboard mockup),
an analytical section (comparison against the industry standard,
a counterfactual scenario), a collected list of rules, and an exercise for
the reader.

Start with the [Introduction](uvod.en.md), or jump straight to
[Chapter 1](poglavlje-01-sta-je-observability.en.md).
