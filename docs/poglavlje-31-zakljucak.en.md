# Chapter 31 — Conclusion: rules collected

An aircraft carries two entirely different systems for recording its own
state — the cockpit instrumentation, which answers questions asked in
advance, and the black box, which doesn't know what will break the flight,
but guarantees that when it does, the evidence will exist. That's the
difference this book began with, because it's the difference that changes
what gets built first.

Thirty chapters later, it's worth saying plainly what hasn't changed since
then: not one tool, not one dashboard, not one architecture described in
this book is valuable on its own. It's valuable only to the degree that it
reliably answers a question nobody knew to ask in advance. Cockpit
instrumentation still has its place — an alert has to know in advance what's
normal, in order to report when something isn't. But every serious
implementation in this book, at some point, hit the limit of the instrument
and reached for the black box — for the ability to ask a question nobody
predicted, about an incident that hasn't happened yet.

What follows isn't a chapter-by-chapter summary. It's a dense list of rules
collected along the way, organized by the book's parts, meant to be torn off
and taped above the monitor — a reference for the moment a decision is being
made, not reading material for beforehand.

## Fundamentals

- Monitoring answers questions asked in advance; observability answers
  questions asked afterward, about an incident you couldn't predict
  precisely enough to build a dedicated alert for — and the costliest
  chapters in any system are the ones nobody knew to ask about in advance.
- The three signals (metrics, logs, spans) aren't three independent tools —
  they're worth exactly as much as they can be tied together through the
  same context, at the same moment of investigation.
- Cardinality is a cost paid in advance for questions you might never ask —
  every new label has to justify its own existence before it goes into
  production, not after.

## Collection architecture

- A watcher's signal must never depend on the infrastructure it watches —
  the alert that tracks whether the observation system itself is alive has
  to have an independent path to a human, because that's exactly the moment
  the standard path is most likely to already be broken.
- The gateway exists to absorb complexity every sender would otherwise have
  to carry on its own — credentials, sampling, routing — but it becomes a
  single point of failure itself if it isn't autoscaled, measured, and
  tested as rigorously as whatever passes through it.
- Without a sidecar collector, the last spans are lost when a job shuts
  down — graceful shutdown has to be proven by measurement, not assumed
  because "it should work."

## Processing, cardinality, cost

- Every cardinality change needs a before-and-after measurement, and a
  trivial rollback — without both, the change is a bet, not an engineering
  decision.
- Sampling at the source has to be aware of what's about to happen, not
  just what already happened — an error occurring for the first time has to
  get through, even when the general rule says "sample it down."
- Observability cost growing faster than the system it's watching is a
  signal in its own right, one that deserves its own dashboard — not an
  incidental line on the monthly bill.

## Alerting, SLOs, incidents

- An alert that never fires is exactly as suspect as a system that never
  goes down — until you've verified it would actually fire when it should,
  silence isn't proof of health.
- An SLO has to be built on a signal resistant to noise that doesn't mean
  failure (restart, deploy, planned maintenance) — otherwise the error
  budget burns on every routine change exactly as it would on a real
  incident.
- A postmortem is the formal channel through which new knowledge enters the
  existing plan — its action items get prioritized like any other work, not
  left in a document nobody tracks.

## Domain case studies

- Two independent observation layers (external and internal) are rarely
  complete without one another — each sees a different class of failure,
  and neither is a superset of the other.
- The completeness model (ran / produced output / why not) is a more
  correct framework for scheduled jobs than the standard pattern for
  services that receive continuous traffic — "finished successfully, but
  empty" has to be treated as a combined condition, never left standing on
  its own.
- An alert about the freshness of data from an external service has to be
  gated on a separate "is the collector alive" metric — without that
  condition, a dead collector looks identical to a catastrophic break in
  the data flow.

## Governance, compliance, maturity

- A PERSON identifier and an ASSET identifier for the thing something was
  done to are different categories — the first gets pseudonymized or
  deleted, the second is deliberately still recorded, because it identifies
  what was done, not who did it.
- What an auditor actually tests isn't whether everything is perfect, but
  the consistency between what's claimed publicly and what's actually
  done — an honest internal status table is evidence of that consistency,
  not an admission of weakness.
- A short, ranked list per domain is only useful if things get removed from
  it once they're actually done — archiving crossed-out items brings back
  the exact noise the list was supposed to remove.
- An AI agent with generic knowledge of observability systems gets you
  exactly to the point where specific insight into your particular system
  is needed — a context layer, not tool access, is what separates a correct
  answer from a confidently wrong one.
- Rollout order into production follows blast radius, not technical
  convenience — the most critical part of the system goes last, as a policy
  written down in advance, not a case-by-case exception.
- A periodic audit has to re-measure EVERY number, not just add new
  findings to the old list — and when a past finding turns out to have been
  wrong, that gets acknowledged openly, with the cause of the error, not
  silently rewritten.

## The last sentence

Not one rule on this list was obvious in advance. Each was learned because
something actually went wrong, or because someone doubted a silence that
looked like health, and checked. That is, at bottom, the entire point of
observability — not a system that knows everything in advance, but a system
that, when the question nobody predicted arrives, has somewhere to go look
for the answer.
