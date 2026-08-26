# Appendix A — PromQL/LogQL recipes

This is a collection of the concrete queries the book relies on, gathered in
one place. Every recipe follows the same shape: the problem it solves, a
query that looks correct but lies, the query that's actually correct, and
one sentence on why the difference matters. It's meant to be opened during
an investigation, not read start to finish.

## 1. Health of a scheduled (batch) job — never the instant value

Jobs that run on a schedule (as opposed to services that continuously
receive traffic) go "stale" between runs — their series naturally disappear
from the latest sample. This lies — it looks like 3 out of 8 job families
are dead:

```promql
count by (job) (batch_step_seconds_count)
```

This correctly measures whether the family RAN in the last 24h, not whether
it exists at this exact instant:

```promql
count by (job) (
  increase(batch_step_seconds_count[24h]) > 0
)
```

**Why:** an instant value doesn't distinguish "paused between two runs" from
"no longer instrumented." For anything scheduled, use `increase([24h])` or
`max_over_time([7d])`, never a bare instant query.

## 2. An empty metric usually means the wrong name, not missing instrumentation

This returns NOTHING — concluding "this isn't instrumented" is premature:

```promql
dremio_memory_heap_bytes
```

The actual metric name, per the OTel semantic convention for JVM memory:

```promql
jvm_memory_used_bytes{service_name="dremio", area="heap"}
```

**Why:** before concluding that something isn't instrumented, read the
expression from an existing alert rule that supposedly tracks that same
thing (`/api/v1/provisioning/alert-rules`) and run THAT expression. If the
alert exists and is working, the metric exists by definition — just under a
different name.

## 3. `or` between two aggregates with the same (empty) label set silently keeps only the left-hand side

Both operands here aggregate away ALL labels down to an empty set, so the
right-hand side matches the left-hand side and `or` keeps only the left —
the other value is SILENTLY dropped, neither summed nor shown:

```promql
count(count by (id) (target_info))
  or
count(count by (id) (max_over_time(target_info[7d])))
```

The fix is a selector that keeps `__name__` (and thereby distinguishes the
series), or two separate queries:

```promql
{__name__=~"target_info"}
```

**Why:** `or` in PromQL isn't "show both" — if the label sets match, the
right-hand side is silently dropped. Never combine different scalar
measurements with `or` without checking that their label sets actually
differ.

## 4. Cardinality by job is a point-in-time value — batch families throw it off by thousands of series

This lies if run at the wrong moment — a batch family paused between runs
can show almost zero "live" series:

```promql
count by (job) ({job="some_batch_family"})
```

Correct for a comparable number:

```promql
max_over_time(
  count by (job) ({__name__=~".+"})[24h:2h]
)
```

Correct for measuring "churn" (how many DIFFERENT job identities rotated
through, not how many exist at once):

```promql
count by (job) (
  count_over_time(target_info[7d])
)
```

**Why:** `max_over_time` can't be applied directly across a selector
spanning multiple metric names — it drops `__name__` and throws the error
"vector cannot contain metrics with the same labelset." The subquery form
(`[24h:2h]`) is the fix.

## 5. A coarse step on a bursty gauge returns all zeros

A 30-day range with a 6h step on a bursty metric returns zero at every
point — it looks like "nothing is happening":

```promql
grafanacloud_logs_discarded_bytes_per_second
```

The fix is to take both the average and the maximum over a finer subquery:

```promql
avg_over_time(
  grafanacloud_logs_discarded_bytes_per_second[30d:5m]
)
max_over_time(
  grafanacloud_logs_discarded_bytes_per_second[30d:5m]
)
```

**Why:** never conclude "nothing is being discarded" from a sampled range
with a coarse step on a bursty gauge — a short, sharp spike simply gets
skipped between samples.

## 6. A counter that's lazily created and disappears on restart

```promql
otelcol_exporter_send_failed_metric_points_total
```

**Why:** this type of counter is only created on the FIRST failure, and
disappears when the job/replica restarts. "The series disappeared" and
"nothing is failing" look identical on a dashboard. Don't read the absence
of a series as proof of health — also check the job's last restart time.

## 7. `deriv()` over JVM heap measures the garbage collector's phase, not a leak

A 7-day `deriv()` on a sawtooth memory pattern depends entirely on WHERE in
the cycle the window starts — this lies:

```promql
deriv(jvm_memory_used_bytes{area="heap"}[7d])
```

**Why:** a heap that grows and then gets cleared by the garbage collector (a
sawtooth pattern) is NOT a leak just because one window shows a rising
trend. The real check: whether the FLOOR (the low point after each GC
cycle) rises across MULTIPLE consecutive cycles — a single window is never
enough.

## 8. "Is anything querying this metric" requires a control query

The query-activity log stream (which records WHO asked, not WHAT they
asked) can't answer "is this metric being used" by searching query text —
because the query text simply isn't there.

**Correct procedure:** the only reliable way is to walk the JSON
definitions of every dashboard (`panels[].targets[]`, recursively through
`row` panels) plus every alert rule (`/api/v1/provisioning/alert-rules`),
searching for the literal metric name. And always run a CONTROL query —
search for the same pattern against a metric you KNOW for certain is in
use. If that one also returns "zero hits," the source simply can't answer
this question at all, and a negative result means nothing.

## 9. Checking whether a signal is passing through the central gateway at all

Whether the gateway is receiving OTLP from sender X at all in the last 15
min:

```promql
sum(rate(
  otelcol_receiver_accepted_spans_total{service_name="X"}[15m]
))
```

Whether the gateway is SUCCESSFULLY exporting onward (not just receiving):

```promql
sum(rate(otelcol_exporter_sent_spans_total[15m]))
  /
sum(rate(otelcol_receiver_accepted_spans_total[15m]))
```

**Why:** "it arrived at the gateway" and "the gateway successfully forwarded
it onward" are two different questions. A ratio below 1 means something is
being lost inside the gateway (sampling, a full send queue, an export
error) — check `otelcol_exporter_send_failed_*` before you suspect the
sender.

## 10. Finding the real metric name after OTLP→Prometheus translation

An OTel metric with a unit in its definition gets a CamelCase suffix when
it lands in Prometheus/Mimir — the unit becomes part of the metric's NAME,
not a label:

```text
OTel:       container.memory.utilized   (unit: MiB)
Prometheus: container_memory_utilized_MiB

OTel:       some.metric.without.unit
Prometheus: some_metric_without_unit_None
```

**Why:** when a query against the "obvious" metric name returns nothing,
first check whether the original OTel definition had a unit — it's
silently turned into a suffix (`_MiB`, `_Bytes`, `_None` for a missing
unit), and that's the most common cause of an "empty metric" that has
nothing to do with Recipe #2 above.

## 11. Cardinality by attribute — before you add it to production

How many DIFFERENT values this attribute would introduce, BEFORE you turn
it on — check against a sample/staging environment, never directly in
production:

```promql
count(count by (proposed_attribute) (some_metric))
```

**Why:** this is a query you run BEFORE the decision to add a new label,
not after — every new attribute value is a new time series, and the cost is
paid upfront, by the number of unique combinations, not by the number of
measurements.

## 12. LogQL — whether one family's logs are arriving at all, correctly parsed

```logql
{service_name="X"}
  | logfmt
  | __error__=""
```

**Why:** the `__error__=""` filter excludes lines that LogQL failed to
parse against the given schema (`logfmt` in this example) — without it,
lines that don't match the expected format silently stay in the result and
can look like everything's fine while parsing is actually failing on every
other line.

---

*Every pitfall listed above comes from a real, documented mistake made
while working on the system this book is based on — each one, at some
point, led to a wrong conclusion before it was caught and written down as a
rule.*
