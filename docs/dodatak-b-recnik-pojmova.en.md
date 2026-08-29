# Appendix B — Glossary of terms

Short, practical definitions of terms used throughout the book — the way
they're actually used in day-to-day work, not encyclopedia entries.
Ordered alphabetically.

**Absence-class alert** — a problem that doesn't manifest as a wrong
signal, but as the **absence** of a signal that should exist (e.g. drift
in alerting coverage). Requires an automated check of the DECLARED
configuration, because observability based on live signals can't notice
something that never started being emitted in the first place.

**Active series / billable series** — active series are time series that
are CURRENTLY receiving data points; billable series are what the
provider actually charges for, and the mechanism linking those two
numbers is rarely fully disclosed. Don't estimate cardinality from the
gap between these two numbers without measuring it directly.

**Adaptive Traces / platform-side adaptive sampling** — a form of trace
sampling where the observability platform, not the collector, decides
what to keep, based on policies that can be changed without redeploying
the sender. The key difference from collector-side sampling: policies
are applied IN ORDER, and the first one that matches wins.

**Attribute / Label** — a key-value pair attached to a metric, log, or
span, saying WHOSE data this is and in what context (e.g.
`service.name`, `http.response.status_code`). A resource attribute (see
below) is a special case that describes the SOURCE of telemetry, not an
individual measurement.

**Blast radius** — how many users/services/records would be affected if
something goes wrong. Used both to order a phased rollout (smallest
radius first) and to prioritize risk (radius × probability × cost to
fix).

**Burn-rate** — how fast an SLO's error budget is being consumed,
expressed as a multiple of the normal rate. A multi-window,
multi-burn-rate design (e.g. 14.4×/6×/3× thresholds) balances fast
detection of severe failures against resilience to short-lived blips.

**Cardinality** — the number of UNIQUE label combinations a single
metric produces. Every new unique combination is a new time series —
cost is charged per combination, not per measurement.

**Collector** — a process that receives telemetry (usually over OTLP),
transforms it as needed, and forwards it onward. Can be a sidecar
(per-task) or centralized (a gateway, shared).

**Dashboard** — a panel made up of tiles, each showing one query
against metrics, logs, or traces.

**Dead man's switch** — an alert designed to FIRE when the mechanism
that would normally report a problem STOPS working — the logic is
inverted from a normal alert: silence is a bad sign, not a good one.

**Dedup** — grouping repeated notifications about the same failure into
a single record within a time window, to avoid flooding a channel with
the same message.

**DPM (data points per minute)** — how many data points per minute a
single series produces; one of the factors, alongside the number of
unique series, that determines billable cardinality.

**Error budget** — the allowed amount of "bad" behavior before an SLO is
breached, derived from a reliability target (e.g. a 99.9% target leaves
a 0.1% budget). Spending the budget is a legitimate currency for
deciding the pace of shipping changes.

**Exemplar** — a single sample (usually one span/trace ID) linked to a
point on a metric histogram, letting you jump from an aggregated graph
straight to a concrete example. Exemplar retention is usually short
(a few hours, for example) — useful for "what's happening right now,"
not for yesterday's incident.

**Exporter** — the part of an SDK or collector whose only job is to
take telemetry that's already been generated and send it onward, in
OTLP format, to the next point in the chain (a collector, a gateway, or
the cloud platform directly).

**Gateway** — a shared component that telemetry from multiple senders
passes through before going on to storage; it does sampling,
authentication, and batching in one place instead of every sender doing
it on its own.

**Golden signals** — latency, traffic, errors, saturation — the core set
of four dimensions for judging a service's health (Google SRE Book).

**Instrumentation** — code, or an agent attached to code, that
generates metrics, logs, and traces from an application's behavior;
can be AUTOMATIC (no code changes) or MANUAL (an explicit line of code
that emits a span or attribute).

**Keyed-HMAC pseudonymization** — turning an identifier into a
pseudonym using a cryptographic hash function with a SECRET key, as
opposed to a bare, unkeyed hash function — the key prevents a
brute-force attack (a dictionary attack) against a known set of
possible values (e.g. email addresses).

**Log** — a text record of ONE specific event, at an exact point in
time; richer than a metric, but harder to search if it isn't
structured and linked to the rest of the system.

**MCP (Model Context Protocol)** — an open protocol that gives an AI
agent structured access to tools and data (in this book: an
observability platform) beyond what the model learned during training.

**Metric** — a single number measured over time (e.g. requests per
second). Cheap to store and quick to graph, but on its own it doesn't
say WHICH request or WHICH user is behind that number.

**Native histogram** — a histogram format where the distribution across
buckets is sent more compactly than in a classic histogram with
fixed, predefined bucket boundaries; it affects billable cardinality
differently from ordinary series (buckets are often billed at a
reduced rate).

**Observability** — the ability to ask a question that WASN'T
anticipated in advance, about an incident that just happened, and get
an answer from data already collected — as opposed to monitoring,
which only answers questions asked in advance.

**OTLP (OpenTelemetry Protocol)** — the standard protocol/format for
sending metrics, logs, and traces between senders, collectors, and the
observability platform.

**POA&M (Plan of Action and Milestones)** — a formal category from the
NIST risk management framework for an item that is NOT YET resolved but
is being actively tracked toward resolution — distinct from formally
ACCEPTED risk, which closes the question by decision, not by deferral.

**Postmortem** — a documented analysis after an incident: what happened,
why, how it was detected, and what changes so it doesn't recur. The
formal channel through which new knowledge enters the future work plan.

**RED method** — Rate, Errors, Duration — the standard framework for
services that continuously receive traffic. Doesn't apply directly to
scheduled (batch) jobs — see "completeness model."

**Resource attribute** — a key-value pair that describes the SOURCE of
telemetry (e.g. `service.name`, `service.instance.id`,
`aws.ecs.task.arn`), as opposed to an attribute that describes an
individual span or measurement.

**Risk acceptance** — a documented decision to KNOWINGLY not resolve a
risk, with a rationale and a date — different from "not done yet,"
which remains an open question. The distinction prevents the same
question from being raised again with every new reader.

**Runbook** — a pre-written set of instructions (usually a decision
tree) for a specific CLASS of failure, not for a single event — used
while the alert is still firing, as opposed to a postmortem, which comes
afterward.

**SDK (software development kit)** — the library an application
includes so it can produce telemetry in OpenTelemetry format at all.

**Semantic conventions** — standardized attribute and metric names that
OTel prescribes (e.g. `http.status_code`), so telemetry from different
systems is comparable without manual mapping.

**Sidecar** — a collector that runs INSIDE the same task/pod as the
application it observes, capturing signals (e.g. the last spans emitted
during shutdown) that a centralized collector outside the task wouldn't
see.

**SLI / SLO** — Service Level Indicator (a measurable signal, e.g. the
percentage of successful requests) and Service Level Objective (a
target value for that signal over time, e.g. 99.9%).

**Span** — one step inside a trace: a single operation or call to one
service, with a duration, an outcome, and its own attributes.

**Span metrics** — metrics DERIVED from spans (traces) before any
sampling — they let a RED dashboard stay full-fidelity even when the
spans themselves are aggressively sampled for storage.

**Tail sampling** — the decision to keep a span is made AFTER the whole
span completes (e.g. "keep all errors, sample the successes"), as
opposed to head sampling, where the decision is made right at the
start, before the outcome is known.

**Target_info** — a standard OTel/Prometheus metric that carries
resource attributes (the source's identity) as labels, separate from
the measured value itself — a common place to check task/instance
identity.

**Tier** — a classification of alerts by severity (e.g.
critical/standard/quiet) that determines whether it gets deduped,
whether it sends a notification at all, and by which path.

**Trace** — a record of the path ONE request took through every
service it passed through, made up of individual spans.

**USE method** — Utilization, Saturation, Errors — a framework for
observing RESOURCES (host, disk, network), as opposed to the RED method,
which observes SERVICES.

**Watcher-outlives-the-watched** — the principle that an alert
monitoring the health of the observability platform ITSELF must have a
path to a human that does NOT depend on that same platform — otherwise,
at exactly the moment it's needed most, it too is mute.
