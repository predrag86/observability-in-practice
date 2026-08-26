# Part II — Telemetry-collection architecture

## Before we start: what exactly we're looking at

Every chapter in this part of the book dives into one specific segment —
the gateway, instrumentation, the sidecar, pull-based patterns, the
frontend, synthetic monitoring — but none of them pauses to show the
**whole picture** before diving into detail. This short, unnumbered
introduction exists to fill that gap: before you follow how each
individual piece is observed, it's worth seeing what those pieces
actually look like together.

The implementation the book follows observes a system made up of several
clearly separated layers, all on AWS except for one deliberate exception:

- **The application layer.** Dozens of backend services (a mix of Java
  and Python, the reason for the two instrumentation strategies from
  Chapters 2 and 5) and frontend applications users open in a browser.
  Backend services are deployed as long-lived container processes; none
  of them talk directly to the cloud observability platform — all of
  them go through the gateway from Chapter 4.
- **The authentication layer.** A self-managed identity provider
  (Keycloak-style), sitting in front of everything that requires login —
  and a subject of observation in its own right (Chapter 20), not just
  infrastructure that enables observing other parts.
- **The data layer.** Two distinct categories, deliberately separated in
  Chapter 7: managed relational databases (RDS/Aurora-style), where AWS
  holds the host and the team has no access to the machine, and a
  self-managed distributed compute cluster (Dremio-style), where the
  team holds both the host and the process.
- **The batch/ETL processing layer.** A fleet of short-lived container
  jobs (AWS ECS/Fargate) numbering in the dozens of independent job
  families — cachers, transformations, report generators — each with its
  own schedule and its own sidecar collector (Chapter 6).
- **The network layer.** Load balancers, NAT egress, private connections
  to AWS services, DNS — the infrastructure carrying everything listed
  above, and a subject of observation in its own right (Chapter 22).
- **One deliberate exception to "everything is on AWS."** An independent
  SaaS data-analytics service (Snowflake-style), living entirely outside
  AWS and outside the network the team controls. This layer first
  appears in Chapter 7 (as the third pull-based pattern) and gets a full
  case study in Chapter 24 — it's introduced here only so the map is
  complete.

The observing side — the gateway, the cloud platform — is deliberately
thin in this diagram, because that's the subject of the rest of Part II.
The point of this overview is the opposite: to show **what** is being
observed, before the book explains **how**.

![The system we observe: the application layer, auth, two types of databases, a batch/ETL fleet, and the network layer — all on AWS, plus one independent SaaS service outside our network. The dashed arrows are the observing side, the subject of the rest of Part II.](diagrams/overview.png){: width="100%" }

This diagram isn't the architecture of the observability system — it's
the architecture of the system **that** the observability system
observes. The distinction is deliberate and worth remembering through
the rest of Part II: every chapter that follows explains one dashed
arrow from this diagram in full depth — why it looks exactly like that,
why it isn't a solid line like the rest, and what would change if it
were.
