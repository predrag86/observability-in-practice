# Chapter 1 — What observability is, and what's just monitoring with a new name

An aircraft has two entirely different systems for recording its own state.
The first is the cockpit instrumentation: airspeed indicator, altimeter, fuel
gauge, cabin-pressure warning. Each of them measures exactly one thing known
in advance, and fires the moment that thing crosses a threshold — when the
instruments were designed, the pilots had to already know what could go
wrong in order to put a sensor on it at all.

The second system is the black box — actually two boxes, the flight data
recorder and the cockpit voice recorder. They report nothing to anyone in
real time. Their only job is to remember absolutely everything — every
flight parameter, every word spoken in the cockpit — so that afterward, an
investigator who had no idea that morning what they'd be looking for can ask
any question in hindsight and get an answer. The black box doesn't know in
advance what will break the flight. It only guarantees that when it does,
the evidence will exist.

That's the difference between monitoring and observability, and it's
operational, not philosophical: monitoring answers questions you asked
*in advance*. Observability answers questions you ask *afterward*, about an
incident you couldn't predict precisely enough to build a dedicated alert
for.

## Before we go further: a few basic terms

Worth naming a few terms right away that we'll use from this point on,
without waiting for a dedicated chapter for each one — just like the pilot
in the example above already knows their instruments before anything goes
wrong.

- **Metric** — a single number measured over time (requests per second,
  CPU utilization, queue depth). Cheap to store and quick to graph, but on
  its own it doesn't say *which* request or *which* user is behind that
  number.
- **Log** — a text record of one specific event, at an exact point in
  time ("14:32:07 — request X returned error Y"). Richer than a metric,
  but harder to search if it isn't structured and linked to the rest of
  the system.
- **Trace** — a record of the path *one* request took through every
  service it passed through, made up of individual steps called
  **spans** — one span per service or operation, with a duration and an
  outcome. The trace with the `records_returned=0` attribute from the
  incident in § 1.2 below is exactly this kind of record.
- **Attribute (label)** — a key-value pair attached to a metric, log, or
  span, saying *whose* data this is and in what context (`service.name`,
  `http.response.status_code`, `records_returned`). Without attributes,
  the three pillars are just three piles of numbers with no context for
  who did what.
- **Dashboard** and **alert** — a panel made up of charts, and a rule
  that fires on its own when a value crosses a threshold; these terms
  already exist in everyday DevOps/SRE work, so this book doesn't give
  them a dedicated definition, but they come up constantly from this
  chapter on.

These five or six terms keep coming back in almost every chapter that
follows. Appendix B, at the end of the book, holds their full
definitions alongside about thirty more specialized terms (cardinality,
tail sampling, burn-rate...) — each of which we introduce only in the
chapter where it first becomes relevant to the story, not before.

## 1.1 The question this chapter answers

Why draw a line between these two words at all, when on the surface they do
the same thing — both say "the system has a problem"? And why is that
distinction important enough to be the first chapter of this book, before
any specific tool?

Because the answer changes **what you build first**. If observability is
just monitoring with a more modern name, then setting up a few dashboards
with metrics and a handful of alerts is enough, and the job is done. If
observability means something structurally different — the ability to ask a
question you didn't know yesterday you'd need to ask — then instrumentation
has to carry context rich enough, from day one, for that question to be
answerable, even when you don't know in advance what the question will be.
That difference in approach doesn't show up while the system is running
normally. It shows up exactly once, in one specific incident, when it's too
late to add.

## 1.2 What that difference actually feels like — one concrete incident

In the implementation this book follows, there's a job everyone on the team
informally calls "the cacher": a scheduled job that periodically pulls data
from an internal service and uses it to populate a cache layer that several
other applications read from. The job has completely standard monitoring: an
alert if the process crashes, an alert if it runs longer than expected, an
alert if it exits with an error.

One morning, that job ran completely "correctly" by every metric monitoring
tracked: it started on time, finished on time, exited with code 0, no alert
fired. And yet downstream applications started returning empty or stale data
to users. The cause: the upstream service, that night, returned an empty but
valid HTTP 200 response instead of the expected list of records — likely the
result of its own brief internal hiccup that resolved itself before anyone
got around to investigating it. The cacher received that empty response,
interpreted it as a legitimate result, wrote it to the cache, and calmly
reported success. From the process's point of view, nothing went wrong — the
only thing that broke was the assumption that "exited without an error" is
the same as "did the right thing."

This is a textbook example of what the literature calls **known unknowns vs.
unknown unknowns**. The "cacher crashed" monitoring alert is a *known
unknown* — the team knew in advance the process could crash, so they put a
sensor on it, exactly like the airspeed indicator in the cockpit. But
"upstream service returns empty-but-valid instead of an error" wasn't
something anyone had imagined precisely enough in advance to build a
dedicated alert for. That's an *unknown unknown* — a category of failure
that better alerts can't uncover, because uncovering it would require
already knowing in advance that exactly this alert needed to exist.

What actually resolved the incident wasn't a new alert — it was a trace that
already existed for that job, with an attribute recording the number of
records returned from the upstream call. Nobody was actively watching that
attribute that morning; after users reported empty data, someone opened that
same trace and within a few minutes saw: `records_returned=0`, on a day when
the average is over 600. The data already existed. Nobody had to know in
advance they'd need it — the instrumentation captured it "just in case," the
same way a black box records every flight parameter whether or not it's ever
used.

After this incident, the team **did not** add a new alert along the lines of
"fire if `records_returned` drops below X" — that would be a natural but
wrong reflex, because it would solve this one specific scenario while the
next unknown unknown would slip by unnoticed again. Instead, they enriched
the set of attributes every similar pull-based job automatically records
(response size, record count, whether the response was empty) — not as an
alert, but as *available context* for the next question nobody has asked
yet. That principle — enrich the data before you know the question, instead
of adding alerts after every incident — runs through the whole book and
comes back explicitly in Chapter 5 (attribute semantics) and Chapter 12
(sampling — because a trace also has to survive long enough for someone to
want to look at it).

## 1.3 Analytical section — where this distinction comes from, and why the three pillars aren't enough

### Known unknowns and unknown unknowns aren't a marketing phrase

The monitoring/observability distinction framed through known-unknown vs.
unknown-unknown isn't a tool vendor's invention — it comes from broader risk
management literature, and was most systematically brought into the software
systems context by the team at Honeycomb (Charity Majors and colleagues),
who use a similar illustration: monitoring keeps track of how many plates to
set for dinner, while observability is what makes sure dinner works out no
matter what happens in the kitchen that night. The point of that analogy is
the same as the black box at the start of this chapter: monitoring is a
prepared answer to a question imagined in advance; observability is the
capacity to answer a question nobody imagined in advance.

This isn't a purely theoretical distinction. It has a direct, measurable
consequence: a system with excellent monitoring but weak observability will
be fast at catching *known* categories of failure (slow response, high CPU,
process crash), and slow — or completely blind — to *new* categories of
failure, even when those new categories are often precisely the ones causing
the most damage, because they happen for the first time with zero defenses
prepared for them.

### RED, USE, and the Golden Signals — an excellent starting point, not a complete answer

When the conversation turns to "what to measure," three methodologies come
up constantly:

- **USE** (Utilization, Saturation, Errors) — Brendan Gregg's framework for
  infrastructure resources: for every resource (CPU, disk, network) track
  utilization, saturation, and errors.
- **RED** (Rate, Errors, Duration) — a framework formulated in 2015 by Tom
  Wilkie (now at Grafana Labs), focused on services rather than resources:
  for every service track request rate, error rate, and duration.
- **The Four Golden Signals** from Google's SRE book — latency, traffic,
  errors, saturation — a conceptual bridge between the previous two,
  formulated somewhat earlier and cited more broadly.

All three methodologies solve the same problem: which **metrics** to define
in advance so that the largest number of common failures is covered with a
small number of signals. That makes them excellent for the **monitoring**
layer — the RED method, for instance, applies directly to every service in
the system this book follows, and is used exactly that way in Chapter 5. But
all three methodologies share the same structural limit: they work with
predefined, aggregated numbers. None of them, by definition, leaves room for
the question "okay, `error_rate` went up — but *for which* requests, with
*which* parameters, from *which* client?" — that question requires a raw,
individual event (a trace, a structured log line) with enough attributes to
filter by, not just an aggregate saying something went up.

That's why a good observability architecture doesn't choose between
RED/USE metrics and observability "instead of" them — it uses both together,
at two different levels: aggregated metrics (RED/USE) as a **cheap, fast
signal that something's wrong** ("error_rate went up"), and richly
instrumented traces and logs as the **mechanism to answer that question**
("which requests exactly, and why"). The first layer says *that* a problem
exists. The second layer says *what* the problem is. A system with only the
first layer knows its kitchen is on fire, but doesn't know where the fire
extinguisher is.

### Why "three pillars" is a list of tools, not a definition

The common definition of observability via "three pillars" (metrics, logs,
traces) is useful as a list of *tools*, but dangerous if read as a
*definition* — because a system can have all three tools installed and still
be a pure monitoring system in practice, if those three tools are only ever
used for questions imagined in advance. The instrumentation that captures
`records_returned` in the cacher example above wasn't part of any predefined
dashboard when the incident happened — it existed because someone had
earlier decided it was worth recording that field "just in case." That
decision, not the mere existence of a tracing tool, is what resolved the
incident in a few minutes instead of a few days of log searching.

It's worth adding a short note on the scope of this list: some vendors —
including Grafana Cloud, the platform this book uses — have recently started
adding **continuous profiling** (Grafana Pyroscope) as a kind of fourth
signal, alongside metrics, logs, and traces. Profiling answers a question
none of the three pillars covers directly: *exactly where in the code* a
process is spending CPU or memory, at the function level, without needing to
know in advance which function to watch. This book doesn't treat it as a
separate topic — the implementation it follows didn't have profiling as an
active part of the pipeline during the period the book describes — but it's
worth keeping on your radar as a natural extension of the same principle:
the more dimensions a system records in advance, "just in case," the better
your odds of answering a question you didn't know yesterday you'd need to
ask.

## 1.4 Rules collected from this chapter

- Monitoring answers questions you asked in advance; observability answers
  questions you ask afterward. You need both — don't pick one over the
  other.
- RED/USE/Golden Signals are an excellent recipe for the *monitoring* layer
  (a cheap, fast signal that something's wrong). Don't try to stretch them
  to do observability's job — that needs a raw, attribute-rich event.
- When you instrument something new, don't just ask "which alert do I need
  here" — also ask "which attribute would I wish I had the next time
  something breaks in a way I can't imagine today."
- A "successful exit" (exit code 0, HTTP 200) isn't the same as "did the
  right thing." For every pull/push job, consider whether there's a silent
  variant of success that's actually a failure.
- Having all three "pillars" (metrics, logs, traces) doesn't guarantee
  observability on its own — what guarantees it is the habit of using those
  tools for questions you didn't anticipate in advance.

## 1.5 Exercise for the reader

Find one scheduled job or batch process in your system that currently only
has monitoring at the "did it crash / did it take too long" level. Ask
yourself: is there a way for that job to "succeed" by the monitoring
definition while still doing the wrong thing (returning an empty result,
processing 0 records, writing stale data)? If there is — that's your
candidate for adding a "just in case" attribute, before you need it, not
after.

---

### Sources used in the analytical section

- [Observability - A 3-Year Retrospective — Honeycomb](https://www.honeycomb.io/blog/observability-a-3-year-retrospective)
- [Monitoring and Observability — Honeycomb blog / docs](https://www.honeycomb.io/blog)
- [The RED Method: How to Instrument Your Services — Grafana Labs](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/)
- [The Four Golden Signals — Google SRE Book](https://sre.google/sre-book/monitoring-distributed-systems/)
- [The USE Method — Brendan Gregg](https://www.brendangregg.com/usemethod.html)
