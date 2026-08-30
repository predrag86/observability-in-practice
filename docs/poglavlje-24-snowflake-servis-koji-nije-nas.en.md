# Chapter 24 — Observing a service that isn't ours (the Snowflake kind)

When a restaurant hires an outside caterer for a big event, that restaurant's
head chef cannot walk into the caterer's kitchen, cannot check the
temperature of their oven, cannot stand next to their cook and watch a dish
being prepared. All the head chef has is whatever the caterer decides to
show them: the bill at the end, the quantity delivered, and, if the caterer
is diligent, a report of what was sent and when. None of it is live — the
bill arrives the next day, the report lags an hour or two. And if the
caterer stops sending reports, that doesn't necessarily mean the food has
stopped arriving — maybe the administrative person who writes the reports
just went on vacation. A head chef who fails to tell the two apart might
conclude the whole event fell through, when in fact the food arrived
perfectly on time — only the report about it didn't.

## 24.1 The question this chapter answers

The last domain case study in this part of the book differs from all the
previous ones in one fundamental way: there is no host to install an agent
on, no process to attach to, no network to observe from inside our own
infrastructure. The service is entirely someone else's — living in the
vendor's cloud, managed exclusively by that vendor. What does it even mean
to "observe" something when we don't have a single one of the usual tools
for doing it?

## 24.2 How it was done — a practical overview

### Zero observability as the starting point

Before this work began, the external data-warehousing service the
implementation uses had absolutely no observability of any kind — not one
metric, not one log, not one alert. All that existed was the monthly bill
and, occasionally, a user's subjective impression that some queries were
"slow." This is a valuable starting point for the chapter — it sets it apart
from every previous case study, where some form of observability already
existed and was being improved.

### Why scheduled collection, not a direct connection

Before any of what's described above was built, three different paths to
the same goal were considered — a dashboard in the observability
platform showing what's happening inside the external service.

The first idea was to install a ready-made connector on the
observability platform for a direct, interactive connection to the
external service, signed and loaded outside the official catalog. This
turned out to be technically infeasible on the platform variant in use
(managed, in the cloud, not self-hosted): the managed variant installs
only connectors from the official catalog, and the mechanism for
privately signing and loading your own connector exists only for the
self-hosted variant of the platform. A dead end, discovered only after
it was attempted.

The second idea was to pay for the official, vendor-provided connector
for a direct connection — technically it would have worked on the
managed platform variant without any obstacles. It was rejected because
it represents a recurring, ongoing cost item, not a one-time build
cost — the budget for it didn't exist.

The third path — the one chosen and built — doesn't use any direct
connector at all: instead of interactive access where someone could
write an arbitrary query and get an answer immediately, a scheduled,
short-lived run periodically pulls the slowest queries from the
service's own, built-in usage history that it already keeps, and pushes
them as sanitized records directly into the observability platform. A
dashboard over those records replaces interactive browsing. The accepted
trade-off is explicit: there's no free, arbitrary querying that a real
connector would give you — what you get is a periodically refreshed
table of the worst queries, not an exploration tool.

### Three phases, one shared session

The solution was built in three separate phases, each covering a different
goal, but all three **share the same session** against the external
service — each phase runs inside the same scheduled, short-lived
invocation, rather than each one opening its own, fresh session:

- **Phase one** — a view of the slowest queries, delivered as searchable log
  entries, with a link back to the service's own diagnostic tool for each
  query.
- **Phase two** — account-level metrics: credits consumed, load per logical
  compute unit, storage footprint, login success rate.
- **Phase three** — data freshness (how old the last loaded row is in each
  key table) and aggregated query-performance figures per compute unit.

Sharing one session across all three phases isn't just a technical
convenience — it was a direct cost decision: because the external service
bills by the minimum activation time of a compute unit, every additional,
separate session would mean paying that minimum charge again. By merging
all three phases into one invocation, the second and third phases cost
practically **zero additional credits** above what the first phase would
have cost on its own.

### How the mechanism actually works, step by step

All three phases from the previous section are executed by the same
mechanism, and that mechanism is worth describing at the "how" level,
not just the "what":

- **Trigger.** A scheduled rule kicks off a short-lived run every three
  hours. A trap worth knowing: an "every N hours" schedule like this is,
  in practice, computed from the moment *the rule itself was created*,
  not from clock midnight — if the rule is ever recreated (not just
  edited), the exact trigger time shifts. Whoever first sets up a
  schedule like this expecting it to land on round hours will be
  surprised.
- **The bookmark of where it left off.** Before each query against the
  external service, the mechanism reads a durably stored bookmark — the
  last row it successfully reached. The query asks only for rows newer
  than that bookmark, with an upper bound on the number of rows per run,
  always oldest first. The bookmark only advances once the rows have
  been successfully delivered to the observability platform — not
  before — so a failed run neither loses rows nor duplicates them.
- **A minimally privileged identity.** The query doesn't run under the
  same identity real applications use, but under a purpose-built,
  read-only identity, limited to only the required view of usage
  history. Authentication goes through a key pair, not a password — a
  leaked credential here opens nothing beyond this narrow view. The
  query itself runs on the smallest possible unit of compute the service
  offers, for the same reason mentioned earlier: minimum billed time per
  wake-up.
- **Sanitization before the data leaves the service.** The text of every
  query is scrubbed of actual values before being sent (concrete
  literals are replaced with a placeholder character), collapsed to a
  single line, and truncated to a reasonable length — what arrives at
  the observability platform is the shape of the query, not the data the
  query ran over.
- **Delivery.** The sanitized rows are sent as logs, through the same
  general protocol this implementation uses everywhere to send logs,
  directly into the observability platform — no intermediary server, no
  temporary file.

The entire run, all three phases together, takes on the order of ten
seconds to a minute — short enough that the code package doesn't even
need to be packaged as a container image. A run that finds no new rows
is entirely routine and quietly finishes with nothing to send — for most
of the day, an earlier run the same day has already picked up everything
that happened that day.

![The concrete data flow through scheduled collection: from the actual query against the external service, through the trigger and the bookmark of where it left off, to sanitized records in the observability platform.](diagrams/ch24-mehanizam-prikupljanja.png){: width="90%" }

### Structural lag, not a design flaw

The implementation explicitly documents that nothing in this system is, or
was ever meant to be, real-time. The data the external service exposes
about its own usage lags anywhere from forty-odd minutes to several hours,
depending on which kind of data is being observed — this lag is a published
property of the service itself, not a consequence of anything in the
implementation. The practical consequence: the threshold for "data didn't
arrive on time" has to be set with a deliberate margin above this published
lag, because a threshold set too close to the actual lag would constantly
false-alert on a perfectly healthy system.

### An alert that depends on the health of its own collector

The most important lesson from this implementation, uncovered and fixed
only after the initial rollout: an alert that tracks data freshness must be
explicitly conditioned on the collection mechanism itself being alive, not
just on whether the observed value has gone stale. The original version of
this alert watched only the age of the freshness metric itself — and once
the collection mechanism stopped running (with no error anywhere in the
call itself, it just quietly never finished), the freshness metric froze at
its last value while time kept passing, which inevitably crossed the
staleness threshold and fired a false, critical alert about a supposed
**complete halt in the data flow** — on a system that was, in reality,
completely healthy. The fix was to make the data-freshness alert explicitly
conditional on a separate "is the collector even alive" metric: without
that condition, a dead collector looks identical to a catastrophic outage
of the data flow from the external service — two entirely different
problems, the same false picture.

### Discovered only after someone finally looked

The mere act of introducing observability uncovered problems that had
existed for months, completely invisible because no one had ever had a
reason to go looking for them: a handful of temporary, "transitional"
tables — leftovers from routine monthly and annual data refreshes — had
never been dropped after the job they were built for finished, amounting
to several terabytes of dead space still being billed every month.
Separately, it turned out that three different environments — development,
test, and production — shared the **same** identity and the same
credential for accessing the external service, stored directly as a plain,
unencrypted environment variable. The practical consequence of this second
finding is serious: a credential leak from the least sensitive, nearly
inactive development environment would, at that point, have been
indistinguishable from a leak of the production credential — because,
technically, they were the same one. Both findings were reported to the
data owners for further decision; observability only made them visible, it
didn't fix them.

![Three phases of collection against an external SaaS service, all three within one shared, short-lived session — the data-freshness alert explicitly conditioned on a separate collector-health metric, so a dead collector is never read as a data-flow outage.](diagrams/ch24-tri-faze.png){: width="90%" }

![When the collector dies, the freshness gauge freezes while time keeps passing — without conditioning on a separate collector-health metric, this looks identical to a real catastrophe on a completely healthy system.](diagrams/dashboard-snowflake.png){: width="95%" }

## 24.3 Analytical section — observability without infrastructure access as a distinct problem

### The service itself distinguishes between two different forms of its own observability

The external service's official documentation draws a clear line between
two entirely separate problems: instrumenting **code that runs inside** the
service (stored procedures, user-defined functions) versus observing **how
the service as a whole is used** (consumption, queries, load, logins). The
service solves the first problem with its own tracing and event mechanism,
built into the platform. The second problem — the one this chapter deals
with — the service solves only through its own queryable views into usage
history. The implementation correctly recognized that its case is
exclusively this second one: the service is used as a data store, not as a
platform on which its own code runs, so the first mechanism simply has
nothing to observe in this case.

### The published lag is officially documented, per view, not assumed

The official documentation for every individual queryable view the
implementation uses states an explicit, numeric value for the expected
lag — from forty-odd minutes to several hours, depending on the specific
view — with a note that these values are "approximate" and that the actual
lag can sometimes be shorter. This directly confirms that the
implementation did not arbitrarily guess at the lag, but pulled it from the
service's own published specification — a principle that should be applied
to every external service whose internal state is observed only through
its own exposed API, not through direct access.

### The "a dead collector looks like a catastrophe" pattern is a known, named problem in black-box monitoring

The broader literature on observing systems without direct host access —
through periodic polling of someone else's exposed API, a common pattern
for any external, managed service — treats the ambiguity of "no new data"
as a well-known, recurring problem: such an alert, by definition, looks
identical whether the upstream service has genuinely gone silent or the
collection mechanism itself has stopped running. The standard, recommended
fix is exactly the one the implementation applied only after its first
false alert — make the staleness alert conditional on the independently
verified health of the collector itself, rather than treating "stale
metric" and "silent upstream service" as the same signal.

### Tuning the minimum activation time has no universally correct value

Both the external service's official documentation and independent
commentary on cloud cost control reject the idea of one universally
"correct" value for a compute unit's minimum activation time — instead,
both sources treat it as a trade-off specific to the workload, between
shutdown speed (less credit wasted while the unit sits idle) and preserved
cache warmth (faster next execution if the unit stays active a little
longer). The official recommendation goes further and explicitly warns
against a mismatched value — keeping a rarely used unit active for too long
burns credits with zero benefit from the cache. This confirms that the
implementation's choice to keep an aggressively short activation time for a
scheduled, periodic job — where there's no benefit from a warm cache
between runs hours apart — isn't arbitrary, but aligned with the workload's
own logic.

### Counterfactual scenario: what would have stayed invisible without this work

Imagine the decision had been "we don't have infrastructure access, so
there's nothing to observe" — a valid-sounding but wrong conclusion.
Several terabytes of unused, forgotten tables would have kept being billed
indefinitely, because no one would have had a reason to look for them
without a systematic review of usage per table. A shared, unencrypted
credential across three environments would have stayed undiscovered until,
in the worst case, a leak from the least-guarded environment turned into an
actual security incident in production. Both findings existed before this
work, entirely invisible — observability didn't create them, it just made
it possible, for the first time, for them to be seen.

Let's return to the restaurant and its outside caterer from the start of
this chapter. The head chef will never be able to walk into someone else's
kitchen — but they can demand a better report, compare it week over week,
and notice when something in that report doesn't add up, even through that
usual, accepted one-day lag. Observing a service that isn't ours will never
be the same as observing our own infrastructure — but not having access to
the host is not the same as not having the ability to find anything out. We
come back to a question posed much earlier in this book: what does it even
mean to "observe" something — and the answer, confirmed here on the hardest
possible example, stays the same. Observability was never about direct
access. It was always about asking the right question and finding **any**
reliable path to the answer, even when that path runs through someone
else's delayed report.

## 24.4 Rules collected from this chapter

- When a service has no host or process you can reach, look for its own
  queryable views into usage history that the service exposes itself —
  that's the only source of truth available, and nearly every serious
  external service has one in some form.
- Pull the published lag directly from the service's official
  specification, for each individual data source — don't assume a single
  lag value applies to the whole service at once.
- Condition every data-staleness alert on an independent check that the
  collection mechanism itself is alive — without that condition, a dead
  collector and an actual outage in the flow look identical, and will
  falsely trigger the most serious alarm possible.
- When billing depends on a minimum activation time, merge all collection
  phases into one shared session instead of letting each one open its
  own — the cost difference can be enormous for a job that would otherwise
  never even notice it's sharing infrastructure.
- Expect that the mere act of introducing observability will surface
  problems that have nothing to do with observability itself — forgotten
  resources, shared credentials — because no one before had a reason, or a
  tool, to go looking for them.
- When a direct, interactive connection to an external service isn't
  available for free (and the paid variant isn't in the budget), check
  whether the external service already keeps its own usage history that
  you can periodically pull and push as logs — a periodically refreshed
  table of the worst cases is often a good enough substitute for free-form
  querying.

## 24.5 Exercise for the reader

List the external, managed services your system uses that you have no host
or process access to whatsoever — a payment service, an email-sending
service, an external data-storage layer, anything living in someone else's
cloud. For one of them, find out whether that service exposes its own view
into usage history that could be polled regularly. If it exists, and no one
is currently using it — that's the gap this chapter is asking you to close.

---

### Sources used in the analytical section

- [Account Usage — Snowflake Documentation](https://docs.snowflake.com/en/sql-reference/account-usage)
- [QUERY_HISTORY view — Snowflake Documentation](https://docs.snowflake.com/en/sql-reference/account-usage/query_history)
- [WAREHOUSE_METERING_HISTORY view — Snowflake Documentation](https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history)
- [Optimizing the warehouse cache — Snowflake Documentation](https://docs.snowflake.com/en/user-guide/performance-query-warehouse-cache)
- [Observability in Snowflake: A New Era with Snowflake Trail — Snowflake Blog](https://www.snowflake.com/en/blog/observability-new-era-with-snowflake-trail/)
- [How to setup a Prometheus dead man's switch](https://jakubstransky.com/2019/01/26/who-monitors-prometheus/)
