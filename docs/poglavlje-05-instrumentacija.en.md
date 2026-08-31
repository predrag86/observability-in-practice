# Chapter 5 — Instrumenting the application: two strategies

A suit bought off the rack is cut for an average build — shoulders, waist,
sleeve length, all tuned to fit the largest possible number of customers well
enough. For ninety percent of occasions, that's entirely sufficient: you put
it on and it looks fine. But for one specific occasion — a wedding, an
important performance — a tailor takes that very same suit and changes only
what's specific to you: the sleeve length, the width across the shoulders,
the exact spot where a button actually needs to sit. The tailor doesn't build
a new suit from scratch. He takes what the factory already does well, and
adds only the one detail the factory can't know in advance, because it's
specific to you.

Instrumenting an application works by the same logic. Auto-instrumentation is
the suit off the rack — it covers what's common to nearly every application
of a given type (HTTP calls, database queries, message queues) and does that
well, without a single line of code in the application itself. What
auto-instrumentation can't know is specific to you: who called this
particular request, and through which channel. That gets added by hand, at
exactly one place, like the tailor's single stitch — not as a new suit from
scratch.

## 5.1 The question this chapter answers

Once the auto-instrumentation from Chapter 2 is set up and working, a natural
question follows: is the job done? Does the application now have "all" the
telemetry it needs, or is there a category of data that auto-instrumentation
structurally cannot see, no matter how well it performs on HTTP calls and
database queries?

The answer determines where the team spends the time that's left: whether it
goes into extending auto-instrumentation to still more libraries (marginal
benefit, since most libraries that matter are already covered), or into a
small number of targeted, manual additions at the points where
auto-instrumentation by definition cannot help.

## 5.2 How it was actually done — a practical walkthrough

The auto-instrumentation from Chapter 2 (the Java agent, the Python SDK with
an entrypoint shim) captures what is **structurally visible from known
libraries**: inbound and outbound HTTP calls, database queries, calls to a
message queue, standard resource attributes set at startup. This covers the
overwhelming majority of what anyone ever looks at on a dashboard or in a
trace during an investigation — and it's deliberately left untouched, not
duplicated by manual instrumentation, because that would be work with no
payoff.

In practice, this is exactly the RED method (Rate, Errors, Duration)
mentioned in Chapter 1 — auto-instrumentation doesn't implement it as a
separate library or extra configuration, it produces it as a byproduct: every
captured HTTP call already carries a duration and a status code, so request
rate, error rate, and duration per service are a query over that same data,
not additional instrumentation work. This holds for the synchronous,
request/response services this chapter deals with; for scheduled batch
workloads without a continuous stream of requests, the same assumption
doesn't hold — see Chapter 23.

There is exactly one category of data that the team, in the implementation
this book follows, consistently adds by hand, on every service: **the
caller's identity and the channel it arrived through.** The reason is
structural, not stylistic — auto-instrumentation sees that an HTTP request
arrived, sees the path and the method, but it does not know, and cannot know,
*who* stands behind that request in a business sense, because that depends on
authorization logic specific to each application. In the system this book
follows, the same endpoint can be called in three different ways:

- a user logged in through the UI, carrying a short-lived session token,
- an external client using a long-lived API key,
- a legacy integration that still sends identity as a query parameter (a
  known, documented piece of technical debt, not an accidental oversight).

For each of these three paths, a small function in the shared middleware
layer extracts the identity — regardless of where it came from — and sets it
as a span attribute (`enduser.id` per the semantic convention, plus an
internal `auth.channel` attribute recording *which* of the three paths the
identity arrived through). This is the **only** manual instrumentation point
in the whole system that is deliberately maintained as such — everything else
is left to auto-instrumentation. It's placed at one location on purpose
(middleware), not scattered across every endpoint separately — so that a
change to the extraction logic (adding a fourth channel, say) requires an
edit in one place, not a search across the entire repository.

An important consequence: because identity becomes a resource/span attribute
on *every* request, a query like "which user hit this slow endpoint" or "how
many errors are coming from this specific API key" becomes a trivial filter
in Grafana Cloud — without it, that data would exist only in application
logs, out of reach of traces and the metrics derived from them (span
metrics, covered in Chapter 6).

![Auto-instrumentation (Java agent, Python SDK+shim) covers everything structurally visible from known libraries; the only manual point is extracting caller identity in the shared middleware layer, regardless of which of the three channels the identity arrived through.](diagrams/ch5-instrumentation.png){: width="92%" }

### When two separate pseudonymization mechanisms don't "know" about each other

The frontend part of the system (covered in detail in Chapter 8) is
deliberately designed to never send a user's real identity into its own
telemetry — it carries only a pseudonymous, technical session ID, with no
name or email address. The backend middleware described above does the
opposite: it extracts the caller's **real** identity (an email address),
because that was the simplest and most useful choice for live debugging —
"which user hit this slow endpoint" is an immediately readable query with no
extra step.

Both designs are, individually, reasonable. The problem is what connects
them without anyone explicitly deciding it: trace context propagation. When
a request initiated in the browser reaches the backend, the standard
span-linking mechanism (trace context propagation) automatically merges the
frontend span and the backend span into the **same** trace — and that's the
whole point of the observability architecture, not a bug. But it means the
merged trace now carries both the pseudonymous ID from the frontend side
*and* the real email from the backend side, on the same, connected path —
two supposedly independent privacy fields, joined by a mechanism that has no
idea privacy is a concern at all.

This wasn't a theoretical worry: it was measured directly, on one real
session, that the frontend-side pseudonymous user ID, followed through the
merged trace, revealed the exact same user's fully concrete, real email
address in the large majority of the connected backend spans — the
frontend's privacy design was working exactly as intended, but the backend
side of the same merged trace was silently undoing it.

The identified fix (not yet implemented at the time of writing) doesn't
touch the frontend at all — it only changes *how* the backend middleware
sets identity: instead of the raw email address, it derives a stable,
non-reversible pseudonym (a keyed HMAC over the normalized email address, so
the same user always gets the same pseudonym, but the pseudonym can't be
reversed into an email without the secret key). The rest of the middleware —
which of the three channels brought the identity, what role and scope it's
assigned — stays completely unchanged. For the rare cases where someone
genuinely needs the reverse lookup (pseudonym → email), a separate,
restricted endpoint is planned with its own authorization and audit log —
resolving identity is itself a sensitive action, not a side effect of
reading a dashboard.

The general lesson goes beyond this one case: when two services
independently decide how to protect identity in their own telemetry, the
mechanism that automatically links them (trace context propagation, but
also a shared dashboard, a shared user identifier in logs) erases the
boundary between them without warning. Telemetry privacy has to be checked
at the level of the **merged** path through the system, not per service
individually — one service "doing everything right" means nothing if its
neighbor at the other end of the same trace reveals what the first one hid.

![Current state: the frontend carries a pseudonymous ID, but the backend middleware from § 5.2 puts a real email onto the same, connected trace — the merged trace is de-anonymized. The identified fix (not implemented) changes only the backend side: the same user gets the same stable pseudonym, and the merged trace stays pseudonymous end to end.](diagrams/ch05-pseudonimizacija-preko-granice.png){: width="80%" }

### When the diagnosis rots out from under you: same symptom, different cause

It's easy to assume that "auto-instrumentation is turned on" means all three
signals (traces, metrics, logs) automatically work for that service, and
will keep working. A real case from one of the batch fleets in this
implementation shows why neither of those two assumptions is reliable: the
environment variable that enables log export had been explicitly set,
confirmed in the job definition, and nothing in the configuration pointed to
a problem — and yet, at the time, not a single log line from that fleet was
reaching the observability platform.

The cause, as diagnosed at the time: the auto-instrumentation library for
that language, in the version then in use, had a dedicated module for the
standard logging module — but that module did exactly one thing: it injected
the current span's identifier into an already-formatted log-line string, so
the log could later be manually correlated with the trace by that
identifier. It didn't add an exporter that would actually send log records
to the observability platform as separate, structured records. The fix was
logged as a known, pending task — manually adding about a dozen lines of
code to establish that missing link.

What happened next is the lesson in itself: that manual fix never actually
had to be written. A few months later, the library was routinely upgraded
for an entirely different reason, unrelated to this problem — and the new
version, as a side effect, started automatically attaching a
structured-record exporter to the default logging system, the moment that
same environment variable was present. Most of the fleet started shipping
logs to the observability platform with zero code changes, without anyone
requesting that as a goal of the upgrade.

When the team, in a later review, went back through the old list of fleets
that "don't send logs," it found that the old diagnosis — "the library
doesn't have that capability" — had in the meantime become wrong for nearly
every fleet on the list, but **not for all of them**. A handful of remaining
fleets still showed the identical external symptom (no logs in the
observability platform), but the cause was no longer the same one: those
fleets are markedly short-lived, and their process exits before the internal
buffer manages to flush what it's accumulated — a mechanism the next chapter
explains in detail. Same symptom, a completely different diagnosis, just a
few months apart.

General lesson: a diagnosed cause has a shelf life. The libraries
auto-instrumentation depends on change versions, sometimes silently fixing
an old bug class as a side effect of a change that never targeted that
problem at all — while the identical external symptom, "no data," in the
meantime starts being produced by a completely different mechanism. Before
reusing an old diagnosis as an explanation, it's worth re-verifying it — not
assuming that the reason that held a few months ago still holds today.

## 5.3 Analytical section — when manual instrumentation is actually worth the effort

### What auto-instrumentation structurally cannot see

Independent analyses of this choice (including Elastic's guide to good
instrumentation practice) name two categories where auto-instrumentation
remains blind, no matter how mature it is: **pure application/business code
that doesn't pass through any known library** (auto-instrumentation attaches
to known libraries — an organization's own business logic simply isn't its
territory), and **context that requires business knowledge** — who the user
is, which tenant, what business category the request falls into — because
nothing in the HTTP call itself structurally carries that without logic
specific to the application. The same analysis recommends that every
organization have a **consistent agreement on resource attributes**
(`service.name`, `service.version`, `deployment.environment`, and a
tenant/organizational identifier where needed) applied across the whole
fleet — exactly the principle this system already adopted in Chapter 2, only
extended here to the *span* level for caller identity, not just the
*resource* level for service identity.

### Where the team deliberately stopped, and why it didn't go further

It's worth explicitly noting what the implementation **didn't** do, because
that's just as important a decision as what it did. The team did not try to
manually instrument "everything that might be useful" — there are no manual
spans wrapping every business function, no attributes manually added "just in
case" outside the middleware layer described above. The reason follows
directly from the lesson uncovered in Chapter 1 (the cacher incident):
enriching context "just in case" is valuable, but only when it's cheap to
maintain. A manual span around every business function isn't cheap — each
one is a line of code that has to be written, reviewed, and maintained
forever, and that goes stale the moment the logic changes and the
instrumentation doesn't keep up. One well-placed enrichment point (the
middleware layer for identity) delivers most of the benefit per unit of
effort; a tenth, a twentieth manually added point delivers steadily
diminishing benefit for the same effort.

### What would have happened with the opposite choice

Had the team gone to the other extreme — relying exclusively on
auto-instrumentation and never adding identity by hand — every investigation
into "who hit this endpoint" would have required cross-referencing a trace or
a metric against an application log by timestamp and request ID, assuming
that log even exists and carries identity in a parseable form. That's exactly
the kind of work done *in the middle of* an incident, under pressure, instead
of existing as a ready-made filter in advance — a cost that, as in Chapter 1,
doesn't show up until it's needed, and then shows up in full.

Conversely, had the team gone to the extreme of manual instrumentation
everywhere — effectively duplicating what auto-instrumentation already does,
plus manual spans around every business function — the result would have
been a greater volume of code devoted to observability than to the business
logic itself, a greater risk of the instrumentation going stale as the code
changes (because a manual span doesn't track refactoring automatically, the
way auto-instrumentation does by attaching to a stable library interface),
and, paradoxically, harder-to-read dashboards — because every team would end
up choosing its own attribute names instead of sticking to a shared
convention, exactly the problem of four different names for the same concept
from Chapter 2.

Back to the tailor from the start of the chapter. He doesn't redo every seam
on the suit — that would cost as much as a new suit, and would destroy the
very thing the factory does well. He changes exactly the one detail the
factory can't know in advance. **Manual instrumentation that tries to replace
auto-instrumentation is wasted time; manual instrumentation that complements
auto-instrumentation at exactly one, well-chosen place is almost always worth
the effort.** The skill isn't in how much you instrument by hand, but in
whether you've recognized *which* one detail matters for your system.

## 5.4 Rules collected from this chapter

- Don't try to manually instrument what auto-instrumentation already covers —
  look instead for what auto-instrumentation structurally cannot see
  (business identity, business category of a request).
- Establish an agreement on resource attributes (name, version, environment)
  across the whole fleet before any team starts adding its own ad-hoc
  attributes for the same concept.
- If you have more than one channel through which identity or context can
  arrive (token, API key, legacy parameter), normalize them at one place
  (middleware), not in every endpoint separately.
- Ask yourself, before every new manual span: "does this complement
  auto-instrumentation, or am I trying to replace it?" — the second answer is
  almost always a sign that the time is going to the wrong place.
- Manual instrumentation that isn't cheap to maintain won't be maintained —
  plan for that from the start, not as an afterthought.
- When two services independently protect identity in their own telemetry
  (e.g., the frontend sends a pseudonym, the backend sends a real identity),
  check privacy at the level of the MERGED trace through context
  propagation, not per service — the mechanism that automatically links
  them has no idea privacy exists as a concern.
- Don't assume a once-diagnosed cause still holds — the libraries
  auto-instrumentation depends on change versions, sometimes silently fixing
  an old bug as a side effect of an unrelated change, while the identical
  external symptom ("no data") in the meantime starts being produced by a
  completely different mechanism; re-verify the diagnosis before reusing it
  as an explanation.

## 5.5 Exercise for the reader

Find one endpoint or job in your system where, in the middle of an incident,
you'd have to manually cross-reference a trace with an application log to
find out *who* triggered the problematic request. If that step exists, it's
your candidate for exactly the kind of targeted manual instrumentation
described in this chapter — one point, one place in the code, consistent
across every path that identity can arrive through.

---

### Sources used in the analytical section

- [Best practices for instrumenting OpenTelemetry — Elastic Observability Labs](https://www.elastic.co/observability-labs/blog/best-practices-instrumenting-opentelemetry)
- [Manual vs. auto instrumentation OpenTelemetry: Choose what's right — Cribl](https://cribl.io/blog/manual-vs-auto-instrumentation-opentelemetry-choose-whats-right/)
- [How to Compare OpenTelemetry Auto-Instrumentation vs Manual Instrumentation — OneUptime](https://oneuptime.com/blog/post/2026-02-06-compare-opentelemetry-auto-vs-manual-instrumentation/view)
- [OpenTelemetry Instrumentation: Manual vs. Automatic — Lumigo](https://lumigo.io/opentelemetry/opentelemetry-instrumentation-manual-vs-automatic-with-examples/)
- [Semantic Conventions for General Attributes (enduser.*) — OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/registry/attributes/enduser/)
