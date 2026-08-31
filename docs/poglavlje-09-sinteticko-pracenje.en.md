# Chapter 9 — Synthetic (Black-Box) Monitoring

A lighthouse keeper doesn't wait for a ship to appear before checking
whether the light works. Every evening, whether or not anyone is visible on
the horizon, he lights it and checks it — because the very night when no
ship is nearby to witness that the light works is the night he most needs
to trust that it will work, for the one ship that does eventually appear,
in the dark, without warning. Had the keeper waited to see a ship before
checking the light, he would have discovered the failure at exactly the
moment it's most expensive to discover it.

RUM from the previous chapter is like a sailor watching the lighthouse from
a ship — he sees it only while he's there, only while there's traffic
generating the signal. Synthetic monitoring is the keeper checking the
light every night, regardless of whether anyone is watching. Both are
needed; they do different jobs.

## 9.1 The question this chapter answers

RUM from Chapter 8 depends on real user traffic for a signal to exist at
all. What happens during a period when that traffic is absent — in the
middle of the night, in the run-up to a launch, in a region where the user
base is small? Does the system then have **no** way at all to know whether
it's working, until the first user shows up to discover that instead of the
monitoring system?

The answer is synthetic monitoring — active, scheduled probes that don't
wait for a real user, but instead simulate one themselves, on a fixed
schedule, regardless of whether anyone is actually using the system at
that moment.

## 9.2 How this was done — a practical overview

The implementation this book follows uses external HTTP probes that **do
not pass through internal infrastructure** — not through the gateway from
Chapter 4, not through the internal network, not through internal DNS. The
probes are run from external locations (managed by the Grafana Cloud
platform itself), hit the application's public endpoints exactly the way a
real user would from outside, and report the result back to the same
observability platform where every other signal in this book lives.

The probes test two different things, deliberately kept separate:

- **Basic availability** — whether the public endpoint responds at all, and
  how long it takes. This is the simplest form of probe and the cheapest to
  maintain.
- **Critical business flow** — a multi-step probe that simulates an actual
  user journey (log in, a key API call, checking that the response contains
  the expected content, not just a 200 status code). This is an important
  difference from a naive availability check: an endpoint can respond with
  200 and empty or wrong content — exactly the same silent-failure pattern
  from Chapter 1 (the "cacher" incident), just applied here to an external
  check instead of an internal batch job.

The probes run from **multiple geographic locations at once**, which gives
a signal that neither RUM nor an internal health check can give in the same
way: if a probe from one region reports a failure while the others operate
normally, that narrows the diagnosis to a network/DNS problem specific to
that region, rather than a problem in the application itself.

The most important architectural property of this pattern, inherited
directly from the principle introduced in Chapter 7 (**the watcher must not
depend on the infrastructure it's watching**): probes run completely
independently of the internal network, the internal DNS zone, and the
internal gateway. That means synthetic monitoring is the only signal in
the entire system that **survives** the scenario in which the whole
internal observability infrastructure is unreachable — exactly the
scenario in which every other source in this book (RUM going directly to
the cloud is the exception, but it doesn't test business logic in the same
explicit way) would fall silent, not because the application went down,
but because the path to the monitoring system went down.

![Probes from multiple regions hit the public endpoint directly over the internet, bypassing the internal network, DNS zone, and gateway — and report the result back to the cloud platform independently of internal infrastructure.](diagrams/ch9-synthetic.png){: width="92%" }

The multi-region setup pays off in exactly a moment like this — when one
region goes quiet while the other two keep reporting normal operation, the
diagnosis narrows itself, without a single additional investigative step:

![Region B stops reporting latency for a short window while Region A and Region C continue normally — a pattern pointing to a regional network problem, not a failure of the application itself.](diagrams/dashboard-synthetic.png){: width="95%" }

### The third layer: does the application actually render, not just does the server respond

The basic availability probe and the business-flow probe still leave one
gap: both test what the server **returns**, neither tests what the browser
actually **shows**. A broken JavaScript bundle — a bad deploy, a changed
path to a static file, an error in the build step — still returns HTTP 200
with a full HTML document; the page itself stays blank, because the script
that would fill it with content never runs. Neither the basic availability
probe (sees a 200, reports "up") nor the business-flow probe aimed at API
calls would catch this — both are looking at the server, and the failure is
purely on the client side.

The implementation this book follows adds a third, separate probe type for
exactly this case: a probe that launches a real headless browser (Chromium,
driven by the same k6 tool behind the business-flow probe), loads the
frontend application the way a real user would, and checks that the page is
actually populated with content after the network goes idle — not just
that a response arrived. This is the same silent-failure pattern from
Chapter 1 and from "critical business flow" above, applied to a third layer
of the system (client-side rendering) that the first two probe types simply
can't see.

Two things are worth stating explicitly about this probe. First: it
deliberately does **not** emit data into the same RUM stream as real users
(Chapter 8) — it would be a synthetic session that quietly polluted the
p75/p95 baseline computed from real traffic, so it's kept entirely
separate, as an independent heartbeat. Second: the browser probe is the
most expensive layer of synthetic monitoring — running a full Chromium
instance per execution carries a much higher cost (both in money and in
generated series/logs) than a plain HTTP probe — so it's deliberately kept
to a minimal footprint that still delivers a signal: one location, an
infrequent interval, instead of the generous multi-region setup the basic
availability probe can afford. The same principle — that frequency and
number of locations directly multiply cost, not just precision — was
already forced into a test once, on the basic HTTP probes in this
implementation, when an over-broad multi-region setup triggered an
unplanned budget overage and had to be trimmed down to a single location at
a longer interval.

### Two depths of the same probe, not two separate alerts

The basic availability probe from the previous section isn't always just one
probe — in the implementation this book follows, the same public
application has **two** HTTP probes, deliberately aimed at two different
depths of the system. The shallow probe hits the root path and checks only
whether the application's shell responds at all — and that can be true even
when the backend part of the system is completely unhealthy, because static
shell content is often served by a layer in front of the application
itself. The deep probe hits a dedicated endpoint that, instead of just
returning "OK," **actually executes** a limited query against the database
the application depends on, and returns an error if that query fails.

The difference in depth isn't cosmetic — it's diagnostic information in
itself, with no additional investigation step. If the shallow probe passes
while the deep one fails, the conclusion is immediate: the application is
reachable, the problem is in the database behind it. If both pass, but the
third probe layer from the previous section — the one with a real browser —
still fails, the conclusion is again immediate: the failure is purely on
the client side, neither the application nor the database has anything to
do with it. This is the same logic already at work for probes distributed
across multiple geographic locations (when one region stays silent while
the others work, it narrows down to a network problem in that region) —
just applied to a different axis: probe depth instead of geography. The
pattern of which layer fails is a diagnosis in itself.

The deep probe also carries its own cost worth acknowledging: since it
actually executes a query, its response time tracks database latency, not
just network latency to the application — which means that probe's timeout
must be wider than the shallow probe's, otherwise every occasional slow
query (not a real outage) will falsely trigger an alert meant to catch
actual failures.

![Three probe layers, each testing a different depth of the system: the shallow probe checks only whether the shell responds, the deep probe checks whether the database behind the application actually works, the rendering probe checks whether the page actually displays. The pattern of which layer passes and which fails is the diagnosis itself.](diagrams/ch09-slojevi-otkaza.png){: width="85%" }

### The same metric, two different thresholds, because they don't answer the same question

The synthetic layer with a real browser from the previous section doesn't
just measure whether the page displays — it also measures the same
perceived-performance metrics (largest contentful paint, layout stability)
that RUM from Chapter 8 already tracks for real users. At first glance that
sounds like duplicating the same signal twice. In the implementation this
book follows, the threshold for that synthetic check is deliberately set
far stricter than RUM's threshold for a "bad" experience — because the
synthetic probe always renders the same, lightweight, unauthenticated home
page, with a stable baseline time far below RUM's "bad" cutoff; any
significant deviation from that stable baseline is a **regression**, not
merely a "bad experience."

The two checks therefore answer different questions, even though they
measure a metric with the same name: the synthetic probe asks "did
something just break relative to yesterday," RUM asks "is the actual
experience of real users, across the full diversity of their networks and
devices, currently acceptable." If the synthetic probe were given the same,
wide RUM threshold, it would lose its purpose as an early regression
signal — a real failure would have to get bad enough to cross a threshold
calibrated for chaotic real traffic before the synthetic probe would even
report it, even though on its own stable baseline it would have recognized
it much earlier.

## 9.3 Analytical section — why synthetic monitoring isn't "poor man's RUM"

### Synthetic and RUM solve different problems, not the same problem two different ways

Independent comparisons of RUM and synthetic monitoring (including
ClickHouse's and MDN's material on the subject) consistently state that
these are two complementary approaches, not competing ones. RUM is better
for understanding **actual** user experience — real devices, real
networks, real geographic distribution, long-tail problems that no
synthetic scenario would ever hit because nobody imagined them in advance
(the same "unknown unknown" problem from Chapter 1, just now at the level
of performance instead of correctness). Synthetic monitoring is better for
**stable, repeatable** availability checks and for alerts that need to work
independently of traffic — SLA verification, off-hours alerting, regression
testing of critical flows before a change is even released to production.

An attempt to replace one with the other always exposes the same blind
spot: a system that relies on RUM alone knows nothing about its own state
when there's no traffic; a system that relies on synthetic probes alone
doesn't see the real distribution of user experience (probes test a
fixed, small number of scenarios from fixed locations — not the chaos of
the real world).

### Why test the business flow, not just availability

It's worth explicitly noting why the decision to have probes test a
**critical business flow**, not just "does the endpoint respond with 200,"
is a direct consequence of the lesson from Chapter 1. Had the probes in the
implementation this book follows checked only basic availability, the
system could have "passed" every probe for days while quietly returning
incorrect or empty responses in the background — the same silent-failure
pattern, just now unnoticed by a tool specifically designed to catch
failures. The extra cost of a multi-step probe (maintaining a test
account, refreshing test data, a slower probe) is accepted precisely
because a simple availability probe gives a false sense of security — it
looks like something is protecting you, when in fact it doesn't catch the
very class of failure that hurts the most.

### What would be lost without this layer

The counterfactual scenario is straightforward: without synthetic
monitoring, the only signal about the system's availability outside
periods of traffic would be silence — and silence, as Chapter 1 showed for
the "cacher" job and Chapter 7 for a database refusing connections, is not
easily distinguished from "everything is fine." The first sign of trouble
would be the first user complaining, instead of an alert that arrived
before any real user had even tried to reach the system. For a system with
business users across different time zones and quiet traffic periods, this
difference isn't cosmetic — it's the difference between detecting a
failure in two minutes and detecting it in two hours.

Let's return to the lighthouse keeper. He doesn't light it because he
expects a ship that particular night — he lights it because he doesn't
know in advance which night a ship will actually come, and the only way to
be ready for that night is for the light to be tested every night, not
just the ones when someone is there to notice. **The value of synthetic
monitoring isn't measured by how often it finds a problem — it's measured
by the fact that, when a problem exists at exactly the moment nobody is
watching, someone still knows.**

## 9.4 Rules collected from this chapter

- Synthetic monitoring must run completely independently of the internal
  network, DNS zone, and gateway — that's the only way it stays useful
  exactly when that infrastructure fails.
- Don't stop at checking basic availability (status code) — test at least
  one critical business flow end to end, verifying that the content of the
  response is actually correct, not just that a response exists.
- Use probes from multiple geographic locations whenever possible — the
  difference in which location reports a failure is itself diagnostic
  information.
- Don't treat synthetic monitoring as a substitute for RUM, or the other
  way around — one sees actual experience, the other sees availability
  independent of traffic; a system without both has a blind spot it
  doesn't know it has.
- Check that your probes actually run during the periods when traffic is
  lowest (night, weekend) — that's the period when their value shows up,
  and the period it's easiest to forget to test.
- Add a layer that actually renders the client (headless browser), not
  just checks the HTTP status — a broken JS bundle still returns 200 while
  the page is blank, and no server-side probe sees that. Keep that probe
  separate from real RUM traffic and at a minimal footprint (one location,
  infrequent interval) — it's the most expensive layer of synthetic
  monitoring.
- When you have a probe that actually executes a query (not just checks
  that a service responds), give it a wider timeout than the shallow
  probe's — its response time tracks the latency of whatever it's
  querying, not just the network latency to the application.
- When the same metric exists in both a synthetic probe and RUM, don't give
  them the same threshold — a synthetic probe on a stable, lightweight
  baseline needs a strict threshold for early regression, RUM on chaotic
  real traffic needs a wider threshold for a genuinely bad experience;
  using the same threshold in both places defeats the purpose of one of
  them.

## 9.5 Exercise for the reader

Imagine your system stops working at three in the morning, in a time zone
where you currently have no users. Go through every monitoring layer you
have and ask the question: would this layer notice the failure at that
moment, or does it depend on some specific actor (a user, a system that
depends on yours) actively using the system right then? If most of your
layers depend on active traffic, that's a sign you're missing the layer
described in this chapter.

---

### Sources used in the analytical section

- [RUM vs synthetic monitoring: which do you need? — ClickHouse](https://clickhouse.com/resources/engineering/rum-vs-synthetic-monitoring)
- [Synthetic and Real User Monitoring Explained — Catchpoint](https://www.catchpoint.com/guide-to-synthetic-monitoring/rum-vs-synthetic-monitoring)
- [Performance Monitoring: RUM vs. Synthetic Monitoring — MDN](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Rum-vs-Synthetic)
- [Synthetic Monitoring vs. Real User Monitoring (RUM) — Kentik](https://www.kentik.com/kentipedia/synthetic-monitoring-vs-real-user-monitoring/)
- [Synthetic Monitoring vs. Real User Monitoring (RUM): A Comparison — DebugBear](https://www.debugbear.com/blog/synthetic-vs-rum)
