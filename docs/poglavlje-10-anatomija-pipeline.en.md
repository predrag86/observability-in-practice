# Chapter 10 — Anatomy of the pipeline: what happens to the signal before it goes to the cloud

A water treatment plant doesn't turn murky river water into drinking water in
one step. The water passes through a series of stations, each with exactly
one job, in exactly this order: first a coarse screen that removes branches
and large debris, before anything else gets a chance to clog; then a
sedimentation basin where sediment naturally settles to the bottom; only then
chemical treatment targeting specific contaminants; finally a filter that
removes whatever is left, and only then does the water go to the reservoir.
The order isn't arbitrary — the coarse screen has to come first, because
without it every station after it would be choked with branches that should
never have made it past the first step.

The telemetry pipeline inside the gateway works on the same logic: the signal
passes through a series of stations, each with exactly one job, in exactly
this order, and the order is just as deliberate a choice as any individual
station.

## 10.1 The question this chapter answers

Chapter 4 showed *that* the gateway does processing before it passes
telemetry onward. This chapter answers the question Chapter 4 deliberately
left unelaborated: **what exactly happens inside the gateway, step by step,
and why in this particular order?** This isn't a cosmetic question — the
wrong order between two otherwise-correct stations can cancel out the purpose
of both, the same way chemical treatment before the coarse screen would just
clog the chemical station with branches.

## 10.2 How it's done — a practical overview

The pipeline inside the gateway, in the implementation this book follows,
has six stations, always in this order:

![Anatomy of the pipeline: six stations, always in the same order.](diagrams/ch10-pipeline.png){: width="98%" }

**1. `memory_limiter` — always first.** Tracks the memory consumption of the
gateway process itself, at short intervals. When consumption crosses a soft
threshold, it starts rejecting new data back toward the sender (instead of
silently dropping it) — so the sender gets a signal to slow down or retry
later. When a hard threshold is crossed, the gateway forces a garbage
collection. It has to be the first station in the chain for one reason: if
any station downstream of it had already spent memory processing a record,
the backpressure would arrive too late to prevent anything.

**2. `filter` — discard noise before anything else spends work on it.** This
is where health-check calls are dropped (an internal load balancer pings the
gateway every couple of seconds — that traffic has no analytical value and
just consumes budget) along with log lines below INFO level. Whatever is
dropped here never reaches the more expensive stations further down the
chain.

**3. `transform` — redaction and normalization, both scoped to the right
part of the fleet.** Two separate jobs live in this station:

- **Redaction of sensitive attributes** (SQL text, connection strings) —
  applied only to the parts of the fleet where the debugging value of the
  full SQL text isn't needed. For the part of the fleet where the full SQL
  text is still necessary for diagnosis (covered in Chapter 18), redaction
  is deliberately **not** applied — a decision made explicitly, per
  team/service, not globally.
- **Normalization of span names** — a span that would otherwise carry a
  variable date or ID in its name (e.g. `process-report-2026-08-21`) is
  normalized to a stable pattern (`process-report`) before moving on.
  Without this step, every new day would literally mean a new time series
  keyed by span name — a cardinality explosion that only becomes visible
  once the bill arrives (covered in Chapter 11).

**4. `resourcedetection` — fill in, don't overwrite.** Adds common cloud
attributes (region, account, infrastructure type) **only where they're
missing** — if the sender has already sent its own value, it's left alone.
This is a deliberate decision: the sender always knows more about itself
than the gateway can guess from the context in which it receives the data.

**5. `batch` — group before sending.** Instead of each individual record
going out as a separate HTTP call to the cloud platform, this station groups
them into larger packages — drastically fewer network calls, drastically
less overhead per record.

One trap discovered in production, outside this usual flow: **a size limit
on individual log messages.** One application, on one occasion, sent a log
line several megabytes in size (a serialized stack trace with the full
content of a failed batch write) — with no upper bound, that single message
consumed enough resources in the `batch` station to slow down, and
eventually bring down, processing for the entire window, including thousands
of other, completely normal messages waiting in the same package. After this
incident, an explicit upper bound on per-message size was added to the
`filter` station — too far down the chain was too late.

## 10.3 Analytical section — why order isn't a matter of style

### The official recommendation on processor order

The official OpenTelemetry Collector documentation explicitly recommends
that `memory_limiter` be the **first** station in every pipeline, for
exactly the same reason applied here: so that backpressure can reach the
receiver before anything downstream spends memory on a record that's going
to be dropped anyway. Independent comparisons (Dash0, OneUptime) add the
other half of the same recommendation: expensive transformation stations
(like redaction or normalization) should come **after** cheap filtering
stations — processing a record that the next step is going to throw away
anyway is pure wasted work.

The implementation this book follows follows this order exactly — which is,
unlike some earlier chapters, a case with no deviation from the "textbook"
recipe. It's worth saying explicitly: **not every chapter has to tell a
story about deviation.** Sometimes the standard recipe is standard precisely
because it solves a real, general problem in the best available way, and the
sign of maturity is recognizing when that's the case — not inventing a
reason to deviate just so the chapter has a more dramatic story.

### Where the implementation does add something the recipe doesn't mention: scoped redaction

Official recipes for redacting sensitive data almost always assume a
**global** policy — one rule, applied to all traffic passing through the
pipeline. That's a reasonable default assumption for most systems. The
implementation this book follows deliberately departed from that assumption,
because a global redaction of SQL text would solve one problem (exposure of
sensitive queries) by creating another, equally real one (the part of the
team that diagnoses problems precisely through the full SQL text would lose
exactly the data that is their job to have). The solution wasn't "redaction,
yes or no" as a binary decision for the whole system, but an explicitly
scoped policy per part of the fleet — administratively a bit more expensive
to maintain (two branches in the configuration instead of one), but it
avoids trading one form of harm for another.

### The cost of a different order: a counterfactual scenario

It's worth playing out concretely what would happen if the `batch` station
came **before** `memory_limiter`, instead of after it. The batch station, by
its nature, holds data in a buffer longer than any other station — it waits
for enough records to accumulate, or enough time to pass, before sending a
package onward. If that buffer came before the memory check, the gateway
could accumulate a large volume of data in the batch buffer at precisely the
moment of pressure when `memory_limiter` would most want to slow the
inflow — the dam would exist, but it would be guarding an empty stretch of
pipe, while the real pressure would already be downstream of it, out of its
reach. This is the same pattern seen elsewhere in this book: a protective
mechanism that technically exists, but is placed at the wrong point in the
flow, provides a false sense of safety with no actual protection.

Let's return to the water treatment plant from the start of the chapter. The
coarse screen isn't the first station because it's the most important one —
the chemical treatment targeting specific contaminants is, by many measures,
a subtler and more valuable station. The coarse screen is first because, if
it weren't, every station after it would be doing work it wasn't designed to
do. **Order in a pipeline isn't a list of priorities — it's a chain of
assumptions, where each subsequent station assumes the previous one has
already done its part.** When that assumption breaks, the cost doesn't show
up at the station that got moved — it shows up at every station after it.

## 10.4 Rules collected from this chapter

- `memory_limiter` (or its equivalent) always first in the chain —
  backpressure that arrives too late is the same as backpressure that
  doesn't exist.
- Filter out noise before doing anything more expensive with a record —
  every station that processes a record the next station is going to drop
  is pure waste.
- Don't apply a global redaction/transformation policy when different parts
  of the fleet have different, legitimate needs — explicitly scope the
  policy, even at the cost of somewhat more configuration.
- Set an upper bound on the size of an individual record as early as
  possible in the chain — one oversized record must not be able to drag a
  thousand valid ones down with it.
- Don't invent a story about deviating from the standard where the standard
  already solves the problem well — recognize when "follow the recipe" is
  the right answer.

## 10.5 Exercise for the reader

Sketch out the order of stations in your own telemetry pipeline (or, if you
don't have one explicitly drawn, the assumed order in which the data is
actually processed). For every pair of consecutive stations, ask: does the
earlier station guarantee the assumption the next one relies on? If any pair
fails that test — that's your candidate for reordering, before production
traffic discovers it instead of you.

---

### Sources used in the analytical section

- [Memory Limiter Processor — OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/memorylimiterprocessor/README.md)
- [Mastering the OpenTelemetry Memory Limiter Processor — Dash0](https://www.dash0.com/guides/opentelemetry-memory-limiter-processor)
- [How to configure OpenTelemetry Collector memory limiter for stability — OneUptime](https://oneuptime.com/blog/post/2026-02-09-otel-memory-limiter-stability/view)
- [Batch Processor — OpenTelemetry Collector Contrib](https://github.com/open-telemetry/opentelemetry-collector/tree/main/processor/batchprocessor)
- [Grafana Alloy documentation — Component reference](https://grafana.com/docs/alloy/latest/reference/components/)
