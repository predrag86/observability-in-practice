# Chapter 13 — Alerting architecture: two paths, one destination channel

An emergency dispatch center receives calls in two entirely different ways.
A citizen picks up the phone and dials — a human voice, describing what they
see, often unsure of the details. At the same time, a smoke detector in a
building on the other side of town sends a signal on its own, automatically,
the moment it registers smoke above a threshold — no words, no person
dialing a number. These two signals share nothing technically — one is human
speech over a telephone network, the other is a machine signal over a
dedicated line — and yet both end up at the same console, with the same
dispatcher, because at that moment the dispatcher doesn't care **how** the
signal arrived, only **that** it arrived. If someone tried to make the smoke
detector "call by phone" for the sake of consistency, all they would add is
latency and a point of failure where none needed to exist.

## 13.1 The question this chapter answers

The system this book follows has alerts that arrive from two fundamentally
different sources — direct infrastructure events (did a container task die)
and signals derived from telemetry (a PromQL query over the metrics that the
gateway from Chapter 4 collects) — and both ultimately land in the same
Slack channels. This chapter answers the question of why those two paths
are deliberately **not** merged into one shared mechanism, and how, within
that dual path, alerts are then distributed to the teams that need to see
them.

## 13.2 How it's actually done — a practical overview

**Path A — direct infrastructure events.** When a container task in the data
processing fleet changes state (stops, crashes, fails to start), the cloud
platform emits an event in real time — no intermediary, no metric that has
to be computed first. That event directly triggers a function that
classifies severity, checks whether the same pattern has already been
reported recently (so a single, identical crash doesn't produce ten
messages), and sends a formatted message with direct links to the relevant
dashboards.

**Path B — signals derived from telemetry.** Applications send their metrics
and traces through the gateway from Chapter 4, which forwards them to the
cloud observability platform. There, a PromQL query periodically checks
whether some condition holds (for example, whether the error rate has
crossed a threshold), and if it does, the platform itself sends an alert to
the same destination.

Both paths ultimately land in the same Slack channels — but **not through
the same mechanism**. This is a deliberate architectural decision, not a
historical byproduct: the signal from Path A naturally lives in
infrastructure events (there's no point converting an event into a metric
just so it can pass through the same pipeline as Path B), and the signal
from Path B naturally lives in telemetry (there's no point pulling it out of
the platform back into the infrastructure layer). Each path follows the
signal to wherever it naturally lives, without an unnecessary cross-cloud
hop.

### Distribution by domain — "the owner of the signal is the owner of the channel"

Alerts are then split by the domain they concern, not by which path they
arrived through. The backend service has its own channel, the database its
own, the auth layer (a Keycloak-type identity provider) its own, the
batch/ETL fleet its own, the network layer its own, the server fleet its
own. The principle is simple: the team that owns a given segment of the
system should see exactly its own alerts, not have to search for them
inside one shared, flooded channel. A signal from Path A (an infrastructure
task crash) and a signal from Path B (a telemetry-derived alert) for the
**same** domain end up in the **same** dedicated channel — the difference in
path is invisible to the team reading the alert, and that's how it should
be.

### The fallback chain — an alert is never lost

Each dedicated channel is actually a separate Slack integration (webhook),
and the mechanism that picks which integration to use works on a principle
of **backward fallback**: first try the dedicated webhook for that domain;
if it isn't configured (empty value), fall back to the next, broader
channel; if that one isn't configured either, fall back to the general,
always-present channel. This means introducing a new domain (a new
dedicated channel) never risks an alert vanishing entirely if someone
forgets to fill in the configuration for that channel in time — the alert
just settles one level wider, never disappearing into silence. This
decision is especially valuable because it runs counter to the intuitive
reflex that "the default route is where alerts we don't want to see go" —
here, the default route is a real, watched channel, not a wastebasket.

![Two independent paths converge on routing by domain ownership, with an explicit fallback chain toward the general, always-watched channel when a dedicated webhook isn't configured.](diagrams/ch13-dual-path.png){: width="95%" }

## 13.3 Analytical section — why they don't merge into one mechanism

### The official recommendation: route by ownership, not by technology

An independent review of alert routing practice consistently recommends a
two-layer approach: coarse routing at the level of the alerting tool (which
platform, which team), and fine routing within that (severity, specific
escalation). Rule order should go from most specific to most general, with
a default route that must **never** be treated as "the place where alerts
we ignore go" — exactly the principle applied in the fallback chain
described above. The same material recommends regularly measuring what
percentage of alerts actually hits a dedicated route versus the default one
— a target of 95%+ coverage by dedicated routes surfaces configuration gaps
before someone discovers them live, in the middle of an incident.

### Why there isn't one universal pipeline

The common impulse is to force everything through a single platform for the
sake of consistency — "everything should go through the observability
platform, for one source of truth." The implementation this book follows
explicitly rejected that impulse for three reasons: first, the state of an
infrastructure task naturally lives in infrastructure events, not in a
metric — forcing it through would mean either publishing those events as log
lines or synthesizing a metric purely so it could pass through the same
pipeline as Path B, an extra hop with no benefit. Second, the webhook URLs
would have to be either configured in both places (duplication, two places
that can drift apart) or one would have to call the other cross-cloud
(additional operational complexity and an additional point of failure).
Third, the message format from Path A (rich, with logic specific to the task
type and direct links) is hard to express through the observability
platform's alerting templates, which are designed for a different kind of
message.

### The cost of a single path: a counterfactual scenario

It's worth playing out the alternative concretely, in which infrastructure
events were forced through the observability platform for the sake of "one
source of truth." Every task crash would first have to be turned into a log
line or a synthetic metric, then wait for the next PromQL evaluation cycle
(latency a direct event would never have had), and the webhook itself would
have to be configured on the cloud platform's side instead of in the
infrastructure account — which means an outage of the cloud platform (the
exact scenario Chapter 4 already cites as a reason for independence) could
take down **both** paths at once, instead of Path A staying independent and
continuing to work while Path B recovers. Consistency of the transport
mechanism would be bought at the price of exactly the independence that
makes the system resilient.

Return to the dispatch center from the start of this chapter. The dispatcher
doesn't insist that the smoke detector "call by phone" so both calls look
the same on paper — it only insists that both, whichever path they arrive
by, end up at the same console, at the right unit, and that neither call
disappears into silence if the line for a given unit is busy. **A
consistent appearance at the destination doesn't require a consistent path
to it — it only requires that no path fail in a way that drags the other
one down with it.**

## 13.4 Rules collected from this chapter

- Don't force a signal through someone else's transport mechanism for the
  sake of consistency — let each signal travel the path where it naturally
  lives (an infrastructure event through the infrastructure path, a
  telemetry signal through the telemetry path).
- Route alerts by domain ownership (who owns that part of the system), not
  by which technical path they arrived through — the owner of the signal
  should be the owner of the channel.
- Never treat the default/general route as a place for alerts you ignore —
  it must be a real, watched channel, because it's where everything that
  doesn't yet have a dedicated route settles.
- Build in an explicit fallback chain (dedicated → broader → general
  channel) so that missing configuration for a new domain redirects the
  alert instead of losing it.
- Regularly measure what percentage of alerts actually hits a dedicated
  route — a drop in that percentage is an early signal that some domain has
  outgrown its current configuration.

## 13.5 Exercise for the reader

Find at least two alerts in your system that arrive through completely
different technical paths (one a direct event, one derived from a query
over metrics). Do both end up at the same, or at least predictably
connected, destinations? If dedicated configuration is missing for one of
them, where exactly does that alert end up — in some actually watched
channel, or quietly nowhere?

---

### Sources used in the analytical section

- [Best practices for alert routing — Grafana Cloud documentation](https://grafana.com/docs/grafana-cloud/alerting-and-irm/irm/guides/best-practices/routing/)
- [Alerting best practices — Grafana documentation](https://grafana.com/docs/grafana/latest/alerting/guides/best-practices/)
- [Mastering incident routing: a critical component in incident management — incident.io](https://incident.io/blog/mastering-incident-routing-a-critical-component-in-incident-management)
- [How to Implement Alert Routing — OneUptime](https://oneuptime.com/blog/post/2026-01-30-alert-routing/view)
