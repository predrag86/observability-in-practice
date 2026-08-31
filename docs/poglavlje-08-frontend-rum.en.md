# Chapter 8 — Frontend / RUM observability

An embassy in a foreign country is, technically, the territory of the home
state — but it doesn't function as that state's domestic postal system. A
letter sent from the embassy doesn't travel through the host country's local
postal system, because the embassy doesn't belong to that system the way a
citizen's mailbox back home does; it travels by a direct, diplomatic line,
because that's the only route the embassy has available to it at all. And the
embassy doesn't have a single communication channel — it has several: routine
correspondence goes one way, urgent courier packages another — and each of
those channels has to be checked **separately** before anything sensitive
passes through it, because a check on one channel doesn't automatically
protect the other.

The user's browser, for the system this book follows, is in a similar
position. It physically lives outside the internal network — it cannot, and
should not, be granted access to the internal gateway from Chapter 4. It has
to travel its own, direct route. And just like the embassy, it has more than
one channel through which data travels — which means protection has to be
applied to each channel separately, not once, in one place, on the assumption
that this covers everything.

## 8.1 The question this chapter answers

Every chapter on telemetry collection so far (Chapters 4-7) assumes that the
sender lives inside a network the team controls — a service, a batch job, a
database, even a cluster. The user's browser breaks that assumption in the
most fundamental way possible: **it will physically never have access to the
internal infrastructure**, no matter how well that infrastructure is
designed. So how do you collect telemetry from a place that, by definition,
you cannot pull into your own network — and what does that change relative to
everything so far in this book?

## 8.2 How it was done — a practical overview

Frontend telemetry in the implementation this book follows goes **directly**
to a hosted RUM collector on Grafana Cloud's side — not through the internal
gateway. This is the only category of sender in the entire system that
bypasses the gateway deliberately, for a reason explicitly mentioned back in
Chapter 4: the gateway lives on the private network, and the user's browser
physically cannot reach it.

What gets collected:

- **Core Web Vitals** — standardized metrics of perceived performance (time
  to first contentful paint, layout stability, responsiveness to
  interaction) that the browser itself measures and exposes.
- **JavaScript errors** — uncaught exceptions, rejected promises, with a
  stack trace and information about the browser/device.
- **User session traces**, linked to the backend trace through the **same
  trace ID** — when the user clicks a button that triggers an API call, the
  RUM SDK injects a trace-context header into that call, so that the entire
  path (browser click → network call → backend processing → response)
  appears as one continuous trace, readable in the same Grafana Cloud
  interface that backend telemetry already uses.

That last point — a shared trace ID across the entire path — is the reason
the frontend chapter belongs in this book at all, rather than in some
separate, isolated topic: even though the transport mechanism structurally
departs from everything else (direct instead of through the gateway), the
*semantics* remain the same OTel semantics from Chapter 2. Same trace ID,
same context propagation.

**Why propagation works without a single CORS change.** By default, the
RUM SDK injects the trace-context header only into calls whose URL is
same-origin as the page itself — cross-origin calls go without it unless
explicitly added to an allow-list. In the implementation this book
follows, this lines up perfectly with the actual shape of the traffic: the
backend application serves the frontend itself (same origin as the page),
and the frontend calls it on relative paths (`/api/...`) instead of
absolute URLs — so every call to the backend is automatically same-origin,
with no CORS change and no allow-list of domains to maintain. When the
backend's Java agent receives that header, its server span becomes a child
of the browser's span — same trace ID, one continuous trace, without a
single line of code written just for this connection.

Cross-origin calls (an identity provider, maps, other third parties)
deliberately go without the trace-context header — not an oversight, but
an explicit decision: turning it on would mean leaking the trace ID to
services outside your own control and creating orphan spans there (spans
with no matching half, because that service never sends anything back
into the same Tempo tenant). Likewise, the additional OTel mechanism for
carrying arbitrary key-value pairs alongside a trace (baggage) is
deliberately not enabled at all — only the trace ID crosses the
browser→backend boundary, nothing more. A smaller leak surface is
deliberately chosen here over greater flexibility.

![The browser goes directly to the hosted RUM collector, bypassing the gateway; backend telemetry still goes through the gateway. Two separate PII protections (native signals versus traces) are deliberately highlighted — that's the incident point from this chapter.](diagrams/ch8-rum.png){: width="75%" }

**Two points for PII cleanup, not one.** This is the single most valuable
practical lesson of the chapter. The RUM SDK has one central function that
intercepts all "native" signals — logs, measurements, errors — and strips
known sensitive values out of them before sending (email addresses in error
messages, session IDs in URLs). That function does exactly what's expected of
it. The problem: **RUM traces do not pass through that same function.**
Traces are generated and sent through a separate part of the SDK
(instrumentation of automatic fetch/XHR calls), which has its own,
independent path to the network — and that path simply bypasses the same
central function. It turned out that URL parameters carrying user
identifiers, which had been dutifully stripped out of logs, were still ending
up in span attributes, because the team's mental model was "I added a PII
filter" instead of the more precise "I added a PII filter **on this
particular data path**." The fix required an explicit, separate redaction at
the span-processor level, not an extension of the existing function that had
never even seen the traces.

Here's what a Core Web Vitals dashboard looks like in practice — three
percentiles (p50/p75/p95) instead of a single line, because an average, or
even a median, can easily hide precisely the segment of users having the
worst experience:

![LCP tracked by percentile: p50 and p75 stay stable, but p95 shows a clear regression on one day — a signal an average would hide, because it hits only a portion of traffic (typically one geographic region or device type).](diagrams/dashboard-rum.png){: width="95%" }

### When the build stays silent about its own failure

The first attempt to ship frontend telemetry into the trial environment
passed, by every standard check, flawlessly: the build passed, tests were
green, the shipped application returned HTTP 200 and worked completely
identically for the user as before. None of those checks caught that the
shipped bundle **contained no telemetry SDK initialization call at all** —
the build had been run from an older version of the source code,
snapshotted before the instrumentation code had even landed on the branch it
was built from. The application behaved identically because telemetry never
affects how the application looks or functions for the user — only whether
anything arrives at the other end, outside the view of any check that only
looks at the delivered page.

It was only caught by an explicit, purpose-built check: searching **the
shipped, already-built JavaScript bundle itself** (not the source code, but
the artifact that actually went to the server) for the name of the function
the SDK calls on initialization, and, separately, checking whether that
frontend service's name shows up at all in the telemetry storage system —
even with zero data points. Both checks were run **after** every standard
check had already declared the release successful. An additional trap
discovered along the way: there's also a separate, entirely distinct system
that also builds a frontend bundle for its own code-correctness check, but
nobody ever actually ships that artifact — an easy mistake would be
assuming "that build passes" means "the shipped build is instrumented,"
when in reality those are two entirely independent artifacts.

General lesson: the presence of the telemetry SDK is invisible to every
ordinary release health check — a passing build, green tests, HTTP 200, a
working application. The only way to catch its absence is an explicit check
that looks at exactly that code in exactly that shipped artifact, or
verifies whether the expected signal actually showed up downstream — and
such a check is rarely run on its own; it has to be added deliberately.

![Standard release checks (build, tests, HTTP 200) don't look at telemetry code — the shipped bundle can be built from an old version of the source, with no SDK initialization, and none of them will notice. It's only caught by an explicit check of the shipped artifact and downstream telemetry.](diagrams/ch08-tiha-praznina.png){: width="80%" }

### When a percentile lies because the sample is too small

An internal tool with a relatively small number of users turned out, after
going live in production, to generate only about a dozen or thirteen Core
Web Vitals measurements **per day** — while the alert tracking regression
watches **p75 over a rolling 24-hour window**. At that sample size, a single
unusually slow session — a user on a weak network, on an older device, in a
background tab — can shift the whole group's p75 from the "good" range into
the "bad" range on its own, with no real change in the application to
justify it.

So the first step in responding to that alert isn't investigating what
changed in the application — it's checking **whether the sample even has
enough data points for the percentile to be trusted**. The alert explicitly
requires a minimum number of measurements in the window before it even
considers firing, precisely because it's known that at this level of
traffic a percentile on its own isn't a reliable signal below that
threshold.

This deepens a principle already mentioned earlier in the chapter — that RUM
has a blind spot when there's no traffic at all. Here the blind spot is
subtler: the alert **did** fire, the percentile **was** computed, but the
number itself — without the context of how many points went into computing
it — can look like a real regression when it's actually a statistical
artifact of too small a sample. Treating every percentile-based alert as
absolute truth, without asking "how many points was this computed from," is
a mistake that stays invisible until the first false alarm gets
investigated all the way through and turns out to rest on a single session.

## 8.3 Analytical section — why a direct connection isn't a compromise but a requirement, and what it means when "one filter" isn't enough

### Why the standard RUM architecture almost always goes directly to the cloud

Independent overviews of RUM architecture consistently note that browser
telemetry goes directly to a hosted collector, not through internal
infrastructure — for the simple reason that internal infrastructure, by
definition, isn't reachable from the public internet in any way a browser
could safely use. Opening the internal network to the public internet just so
the RUM SDK could send data through "the same gateway as everything else"
would mean breaching precisely the perimeter Chapter 4 so carefully closed —
a cost greater than any benefit gained from transport-path consistency. This
is a rare case where "industry standard" and the implementation this book
follows are **not in tension** — both take the same route, for the same
reason.

### Why RUM and synthetic monitoring aren't substitutes for each other

Independent comparisons of RUM and synthetic (black-box) monitoring — a topic
Chapter 9 covers in detail — point out that RUM depends entirely on real
traffic: the signal exists only if some user happens to be using the
application at that moment. That means RUM has a structural blind spot during
periods of low traffic (nighttime, the run-up to a launch) — if the
application breaks exactly then, RUM simply won't register it in time,
because there's no one there to register it. This blind spot isn't a flaw in
the RUM implementation — it's a structural property of passively observing
real users, and it's solved by combining RUM with active probes, not by
fixing RUM itself.

### The lesson from the PII incident: why "I added a filter" rarely means "everything is covered"

This is the chapter where a principle running through the whole book shows
most clearly — one first named explicitly in Chapter 1, on a different
example: a system can "work correctly" by every check anyone ran against it,
and still miss something none of those checks was even looking at. The PII
filter for logs was tested, it worked, it passed code review — everything
exactly as it should be. What was never explicitly checked was the question
"through **all** of which data paths does this SDK send something to the
network" — and the answer was two, not one, and nobody actively went looking
for the second one, because the first filter "felt like" a complete
solution.

Counterfactually: had the team mapped **all** of the RUM SDK's outbound paths
from the start, before writing the first filter (instead of writing the
filter for the path that came to mind first — logs), this incident probably
would never have happened. The cost of that upfront mapping was small — a
couple of hours reading the SDK's documentation. The cost of discovering it
after the fact was larger: an audit of historical data to estimate how long
the leak had been going on, an extra round of review for the same class of
bug elsewhere in the system.

Back to the embassy from the start of the chapter. It doesn't have a single
communication channel — it has several, and each has to be checked
separately, because a check on one channel doesn't automatically carry over
to another. **When you're protecting sensitive data, the question isn't "did
I add a filter" but "did I enumerate every path a piece of data can leave by,
and does each one of them have its own, explicit check."**

## 8.4 Rules collected from this chapter

- Browser telemetry goes directly to a hosted collector — don't try to force
  it through internal infrastructure for the sake of transport-path
  consistency; that's the wrong kind of consistency.
- Keep the same trace ID and context semantics (OTel propagation) even when
  the transport mechanism structurally differs from the rest of the system —
  that's what ties frontend and backend into one readable trace.
- Lean on same-origin propagation whenever possible (backend serves the
  frontend, calls on relative paths) — it needs no CORS change at all.
  Don't turn on propagation to cross-origin third parties or baggage
  without an explicit reason — each one widens the leak surface for trace
  context beyond your own control.
- Before writing a PII filter, map **all** the outbound data paths of the
  SDK or library you're protecting — logs, measurements, errors, and traces
  rarely share the same processing function.
- RUM doesn't replace synthetic monitoring, nor the other way around — RUM
  depends on real traffic and has a blind spot during quiet periods; that's
  not a bug, that's the reason Chapter 9 exists.
- After every "I added a filter for X," explicitly ask: through which paths
  can X possibly leave at all, and did the filter actually cover every one
  of them.
- No standard release check (build, tests, HTTP status, visible application
  behavior) catches the absence of telemetry code — add an explicit check
  that looks at the shipped artifact itself or confirms the expected
  service shows up downstream.
- Before trusting a percentile-based alert as a real signal, check how many
  points went into computing it — at low traffic, a single session can
  shift p75 from the "good" range into the "bad" range with no real change
  in the system.

## 8.5 Exercise for the reader

Take any library or SDK in your system that sends data to an external
service (RUM, analytics, error tracking) and list **every** type of signal
that library sends (logs, metrics, errors, traces, session replay if it has
one). For each type, check independently whether it goes through the same
sensitive-data filter as the others, or has its own, separate path. If you
can't answer with confidence for at least one signal type — that's the gap
this chapter is asking you to close before someone else discovers it instead
of you.

---

### Sources used in the analytical section

- [What Is Real User Monitoring (RUM)? — Dash0](https://www.dash0.com/faq/what-is-real-user-monitoring)
- [OpenTelemetry for Web RUM — RUM Architecture, Tooling & Self-Hosting](https://www.rum-core-web-vitals.com/rum-architecture-tooling-self-hosting/opentelemetry-for-web-rum/)
- [RUM vs synthetic monitoring: which do you need? — ClickHouse](https://clickhouse.com/resources/engineering/rum-vs-synthetic-monitoring)
- [Performance Monitoring: RUM vs. Synthetic Monitoring — MDN](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Rum-vs-Synthetic)
- [Real User Monitoring (RUM) — OneUptime](https://oneuptime.com/product/rum)
