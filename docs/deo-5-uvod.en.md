# Part V — Domain case studies

## Before we start: the same layers, now as the subject, not the observer

The introduction to Part II mapped the system this book observes: the
application layer, the authentication layer, two kinds of databases, the
batch/ETL job fleet, the network layer, and one independent SaaS service
outside our network. In Part II that diagram was deliberately thin on the
observing side — the point was to show **what** is observed, not **how**.
Part V is where that flips: each chapter takes one of those layers and
questions it in full depth — what specifically breaks the signal here,
and why the standard approach from Parts I–IV isn't enough without
adaptation:

- **Chapter 18** — managed databases (RDS/Aurora-style), where AWS holds
  the host and the team has no access to the machine.
- **Chapter 19** — a self-managed distributed cluster (Dremio-style),
  where the team holds both the host and the process, with everything
  that entails.
- **Chapter 20** — authentication and IAM (Keycloak-style), the layer
  that makes observing everything else possible, and is itself rarely
  the subject of observation.
- **Chapter 21** — hosts and servers as machines, the layer underlying
  everything listed above.
- **Chapter 22** — the network as its own observation plane, the
  infrastructure carrying every other layer.
- **Chapter 23** — the batch/ETL job fleet, where success isn't measured
  by whether the process ran, but by what it produced.
- **Chapter 24** — a service that isn't ours (Snowflake-style):
  observation with no operational control at all over the
  infrastructure carrying it.

This is the longest part of the book, and that's not an accident: it
doesn't introduce a single new observation mechanism — it shows that the
same mechanism, applied to seven different domains, demands a different
decision seven times over. Part VI, which follows, assumes all these
layers are technically covered, and asks a completely different kind of
question: can the system we built be trusted.
