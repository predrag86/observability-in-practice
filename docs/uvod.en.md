# Introduction

Most observability literature explains concepts — the three pillars
(metrics, logs, traces), the RED/USE methodologies, what OpenTelemetry is.
That's necessary, but not sufficient: the real problems start after the
agent is installed — when Mimir doesn't promote the attribute you expected
into a label, when cardinality eats a week's budget over a single weekend,
when an alert that looks correct stays silent exactly when it's needed most,
or when you have to explain to an auditor why a user's email address ended
up in a trace.

This book starts from that other point: from a real, multi-month rollout of
observability **company-wide**, not one demo service in one repository. The
implementation the book follows as its central case study covers dozens of
backend and frontend applications (APM — application performance
monitoring), network infrastructure, managed databases, a self-managed
distributed compute cluster (Dremio-style), an authentication layer, and a
fleet of batch/ETL jobs numbering in the dozens of independent job
families — all on AWS.

A particular part of the story, different enough to earn its own chapter, is
onboarding a service that is **not** on AWS and not hosted internally: an
independent SaaS data-warehouse offering (Snowflake-style). That service has
no host you can install an agent on, no process you can direct to export
telemetry, no network the infrastructure team has visibility into —
everything known about it comes from the system views the service itself
voluntarily exposes, polled from the outside, on a schedule, with a delay
that's structural and can't be eliminated. Chapter 24 covers that story in
full depth: how you collect telemetry for a service you have zero
operational control over, and what that changes relative to everything else
in the book. That distinction — instrument what you control, observe from
the outside what you don't — runs through the whole book as a recurring
theme, and comes back several times even before Chapter 24 (with databases,
with pull-based patterns, with synthetic monitoring).

## Where the material comes from

Every technical example in this book — architecture, PromQL query,
configuration snippet, incident, decision and its analysis — comes from a
real implementation, documented the way it actually happened: with mistakes,
dead ends, revisions, and "why we tried this first, then dropped it" notes.
Nothing in the book is a lab example built to look good in a book; all of it
went through production.

Because of that, one explicit step was taken before publication: **removing
every identifying detail.** The company name, people's names, internal
domains, AWS resource IDs, addresses, names of internal repositories and
applications — all of it was either removed or replaced with generic,
fictional names. What remains are the **patterns and decisions**, not whose
they were. Wherever possible, real numbers were kept (prices, percentages,
timings), because without them half the lessons in the book lose their
point — but never in a way that would reveal which company this is.

## Who this book is for

First and foremost, DevOps/SRE engineers who are building or inheriting an
observability system and want to see what it looks like once it stops being
a prototype. Next, backend and frontend developers instrumenting their own
service who want to know what's actually necessary versus what's cargo-cult
ritual. And finally, team leads who need to make — and justify to a
budget — the decision between Grafana Cloud, competing SaaS platforms, and a
self-hosted setup; that question is such a common first obstacle that it gets
an entire chapter of its own, before the book even gets into technical
detail.

## How the book is organized

Every chapter follows the same pattern, deliberately repeated throughout the
book so reading becomes predictable: it opens with a real-life parallel that
introduces the mechanism in question, moves into a **practical section** —
exactly how it was done in the implementation the book follows — then into
an **analytical section**, where that solution is compared against what the
industry calls "standard," explicitly naming where the implementation
diverged and why, and what would have happened if it hadn't. The chapter
closes by returning to the opening parallel, a short list of rules, and an
exercise the reader can apply to their own system right away.

This format isn't a stylistic choice made for variety's sake — it's a
response to what makes most observability literature weak: it describes
*what* was done, rarely *why exactly that way*, and almost never *what would
have broken had it been done differently*. This book tries to leave every
chapter with exactly that last question answered.

Let's begin.
