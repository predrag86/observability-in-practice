# Chapter 27 — Prioritization: cost, performance, reliability, security

The manager of a large estate with a dozen buildings doesn't keep one
endless list of "everything that should be fixed" — over a year such a list
would grow to hundreds of items, and no one would actually read it anymore.
Instead they keep a short, constantly refreshed list of the ten or so things
being worked on next: a roof that leaks badly if it rains this week goes
above a fence that's been crooked for three years and can probably wait
another one. Once the roof is fixed, it's struck from the list — not moved
to a "done" archive nobody reads, it simply disappears, and the next item
climbs up to take its place. Some items from the bottom of the original list
of a hundred deliberately stay there, with a reason written down: "the fence
waits because the cost of replacing it exceeds the value of that section of
the yard." That is not the same as "we haven't gotten to it." A manager who
mixes up those two reasons eventually loses the owner's trust — either
justifying something that shouldn't have been justified, or forgetting
something that should have been done.

## 27.1 The question this chapter answers

An observability program generates more findings than any team can resolve
at once — security holes, expensive queries, fragile points of reliability,
performance that could be better. What does a living document look like
that ranks the next dozen or so things per domain, with a methodology that
distinguishes an "honorable mention" from an actual priority, and why does
an observability program never "finish," but instead gets managed like any
other backlog?

## 27.2 How it's done — a practical overview

### Separate lists per domain, the same discipline

The implementation keeps a separate, short, ranked list for each of several
domains — security, performance, reliability, cost — instead of one shared
list everything flows into. Each list is deliberately short (a dozen to
fifteen items), drawn from a much wider, detailed backlog where the full
descriptions of findings and runbooks live. The short list is a **view for
deciding** — what to do next, with a clear reason why exactly that item is
at the top. The full backlog is a **store of detail** — where someone goes
when they need the exact step-by-step for a specific item.

### Ranking along three axes, not by a single impression

The order on each list isn't a subjective impression of "what looks urgent."
It combines three independent axes: how far the damage reaches if the
finding is exploited or manifests (blast radius), how likely it is to
actually happen given the current controls, and how quickly/cheaply it can
be fixed. When two separate findings actually share the same root cause, the
implementation deliberately merges them into a single, higher-ranked
combined item — instead of counting them as two separate, lower-ranked
problems. This prevents a situation where the ranking would be falsely low
just because one cause happened to produce several individual symptoms.

### "Honorable mention" as a formal, named category

Below the threshold for entering the main ranked list, the implementation
keeps a separate, named section for items that are real but not ranked high
enough to make the top list. This section has an explicit purpose: when the
main list shortens (items get finished and struck), the next item for
promotion comes from here, instead of the list being artificially padded
with lower-value items just to have ten rows. Distinguishing "honorable
mention" (considered, deliberately ranked lower) from "never even mentioned"
is itself information — it tells the team that something was seen and
assessed, not missed.

A concrete example of what this category looks like in practice, not just
in theory: continuous profiling (CPU/memory at the line-of-code level, not
just the request level) is a capability the observability platform this
book follows already offers — the data source exists, ready to use — and
yet no service is instrumented to use it. This isn't an oversight nobody
noticed: a formal review of the program explicitly listed it with a "gap"
status, not as something that had simply slipped from view, and assigned
it a spot in the second wave of priorities — after items with a larger
reach of damage or higher likelihood, not because profiling has no value.
The recommended next step is already written down and waiting on the
list: turn it on first for the endpoints that already have a defined error
budget (Chapter 15), where linking the trace to the profile would let a
slow call, caught by an exemplar (Chapter 11), be traced not just to the
trace but to the exact line of code that spent the time. The difference
between this and "never even mentioned" is exactly what this section
preserves: someone considered it, wrote down the reason, and left a clear
next step ready for the day the item gets promoted.

### Deletion as the rule, not the exception

Once an item is finished, it is **deleted** from the list — not moved to a
"done" archive, not left crossed out at the bottom. This is a deliberate
discipline: a list that only grows, even with crossed-out items, gradually
turns into something no one actually reads, because the signal-to-noise
ratio keeps getting worse. A short, active list that keeps emptying and
refilling stays something the team actually consults before deciding what
to do next.

### Recording the history of decisions, not just the current state

Every list carries a short, chronological changelog at the bottom — what
was added, what was removed, and **why**, with a date. This isn't
administrative formality: when someone asks months later "why was this item
a priority and that one wasn't," the answer exists, instead of having to be
reconstructed from memory. The changelog also captures the cases where one
item was discovered as a **consequence** of work on a completely different
one — a signal that the domains aren't actually isolated, they're only
presented that way for clarity.

![A living, ranked list per domain: the main top list, "honorable mention" below the threshold as a source for promotion, and the full backlog as a store of detail — three layers, one discipline of deletion once something is actually finished.](diagrams/ch27-tri-sloja.png){: width="88%" }

### Blast radius is measured, not assumed

The first of the three ranking axes — blast radius — sounds like something
eyeballed from the problem's title. The implementation showed, on one
concrete finding, why that isn't enough. The authentication database sat
in a single availability zone, with no replica in another — at first
glance a narrow finding, "authentication can fail." Ranked as medium
severity, because "auth SPOF" sounds like something that hits login, not
the entire product.

When someone actually mapped which API calls depend on authentication —
not an assumption but an actual inventory of routes and their
dependencies — it turned out that literally **every** API call goes
through a check against that database, not just login. The blast radius
thereby changed from "auth goes down" to "the entire product goes down,"
while the fix — adding a replica in a second zone — stayed the same, a
cheap change of a few tens of dollars a month. The ranking changed not
because the problem got bigger, but because only the measurement revealed
how big it had been all along. The implementation explicitly recorded
this alongside the finding: the estimated blast radius was wrong until
someone actually measured it, and that gap is a cheap lesson only because
it was caught before an incident, not during one.

![The same finding, the same fix — but the blast radius changed from "auth goes down" to "the entire product goes down" only once someone actually inventoried the dependencies instead of assuming them from the problem's title.](diagrams/ch27-domet-stete.png){: width="82%" }

### Deleted only once measurement confirms it, not once code lands on a branch

The rule "delete an item once it's finished" from the previous section
sounds simple, but the implementation showed, on one finding, exactly
where the real boundary of "finished" sits. A performance finding
described that a backend service, on **every** basic-auth request,
re-queries the authentication service with no caching at all — adding
measurable latency to every such call and loading the database behind it,
the same one from the earlier example. A fix was proposed, code was
written, reviewed, and **merged** into the development branch.

The item stayed on the list. Not because nobody got around to deleting
it, but because merged code on a development branch isn't the same as
code running in production — the path from the development branch to
production runs through additional release steps, and until that path is
completed, the load on the authentication service in production stays
unchanged. Every item on the list carries its own **verification
signal** — a concrete metric proving the fix actually changed the
system's state, not just that the code reached the main branch. For this
finding, the signal was the call rate to the authentication service
dropping to a fraction of its previous value, measured after the release
to production — only then was the item actually deleted from the list.
The difference between "the code is merged" and "the signal has been
measured" is the difference between two distinct, easily conflated
meanings of the word "finished" — and the implementation deliberately
picks the stricter of the two as the condition for deletion.

## 27.3 Analytical section — a familiar pattern from risk management, applied consistently

### Combining reach and likelihood is a standard, named methodology

The dominant pattern in risk-assessment literature — security and project
alike — combines **reach of damage** and **likelihood** into a single
composite score, sometimes with a third axis of fix cost added afterward for
prioritization. A well-known security methodology formalizes this
explicitly: risk as the product of likelihood and impact, with the note
that the most severe risks should be fixed first, but also that the cost of
fixing must be weighed against the loss — some risk is "reasonable to
accept" if the cost of fixing it is disproportionate. This confirms that the
third axis (speed/cost of fixing) the implementation uses isn't a departure
from the standard — the standard already anticipates it.

### "Accepted risk" is a formal category in two independent standards

Both major risk-management frameworks I researched treat **acceptance** as
one of a small number of formal, named outcomes — not as the absence of a
decision. One framework explicitly requires acceptance to be a "deliberate
and informed decision," clearly separated from passive neglect. The other
goes further: it requires the risk owner to formally approve the residual,
accepted risk, and requires the risk register to record the description,
the score, the chosen treatment, and the status — making "formally accepted"
a measurably different, verifiable state from "still unresolved." This
confirms exactly the distinction the implementation makes between an
"honorable mention" and simply being absent from the list.

### Deduplication before ranking is standard vulnerability-management practice

The broader practice of managing security findings treats merging findings
that share a root cause as a mandatory step **before** ranking, not after —
with the explicit reasoning that ranking before merging means ranking the
same problem multiple times, which defeats the purpose of ranking. A more
advanced approach in the same literature goes further than mere merging:
instead of tracking many surface-level findings, it collapses them into a
single, higher-ranked item tied to the shared root (a vulnerable library, a
misconfigured base image) — because fixing the root resolves all the
dependent findings at once. This is exactly the pattern the implementation
applies when it merges findings that share a cause.

### Two-tier documentation has a formal name in project-management practice

Standard project risk-management practice draws an explicit distinction
between the **risk register** (the central record of all risks, full
detail — cause, likelihood, impact, response plan, owner, status — for the
working team's operational use) and the **risk report** (which pulls the
key information out of the register into a shorter, curated form for
stakeholders, without the full detail). Neither replaces the other — the
register is the source of truth, the report is a decision-making tool
derived from it. This is the formal name for exactly the split the
implementation uses between the short ranked list and the full backlog.

### Counterfactual scenario: what a single, undifferentiated list would miss

Imagine a team keeping one single, large list of every finding from every
domain, with no split into a short list for deciding and a full backlog for
detail, and with no formal "honorable mention" category. The list would
grow until it became hundreds of rows — at which point no one actually
reads it anymore before deciding what to do next; decisions start getting
made by impression, or by whoever last mentioned a finding out loud in a
meeting, rather than by a consistently applied methodology. Deduplicated,
consistently ranked findings would get mixed in with un-deduplicated noise,
and the team would rank the same underlying problem several times, in
several different guises, without ever noticing it was the same problem.

Let's return to the estate manager from the start of the chapter. Their
short list of a dozen items doesn't mean the estate has only ten problems —
it means someone decided, with a clear methodology, which of a hundred
possible items deserves attention this week, and why. An observability
program, viewed as a risk-managed backlog rather than a one-time project,
works by the same rule: it never finishes, because an estate never stops
needing upkeep — but the discipline of ranking and deleting is what keeps
the list useful instead of letting it become just another document no one
reads.

## 27.4 Rules collected from this chapter

- Keep a short, actively maintained ranked list separate from the full
  backlog — the short list is for deciding what to do next, the full
  backlog is a store of detail and runbooks.
- Rank by a combination of reach of damage, likelihood, and cost of fixing
  — not by a single impression of urgency — and merge findings that share a
  root cause before ranking, not after.
- Keep a formal, named "honorable mention" category below the threshold of
  the main list — distinguish "considered and deliberately ranked lower"
  from "never mentioned at all," because that distinction is itself
  valuable information. For every
  such item, write down a concrete next step too, not just the reason for
  deferring it — on the day the item gets promoted, that step should
  already be waiting, ready to go.
- Delete items from the list once they're actually finished, instead of
  piling them up in a crossed-out archive — a list that only grows
  gradually stops being something the team actually consults.
- Keep a short, dated changelog for each list — what was added, what was
  removed, and why — so that the answer to "why was this a priority" still
  exists months later, instead of having to be reconstructed from memory.
- Measure blast radius instead of assuming it from a finding's title — a
  narrow, medium-ranked problem sometimes turns out to hit the entire
  system only once someone actually inventories the dependencies, not
  before.
- Define a concrete verification signal for every item on the list — a
  metric proving the fix actually changed production's state — and delete
  the item only once that signal is measured, not once the code is merged
  into a branch; "merged" and "released to production" aren't the same as
  "finished."

## 27.5 Exercise for the reader

Look at your team's backlog of findings — security, performance, or any
other kind. Is there a short, ranked list separate from the full detail,
with a clear ranking methodology? Is there a formal distinction between
"deliberately deferred, with a reason" and "haven't gotten to it yet"? If
neither of those exists, that's the gap this chapter asks you to close —
not by adding yet another list, but through the discipline with which the
existing list is maintained.

---

### Sources used in the analytical section

- [OWASP Risk Rating Methodology](https://owasp.org/www-community/OWASP_Risk_Rating_Methodology)
- [NIST — Risk Response (glossary term)](https://csrc.nist.gov/glossary/term/risk_response)
- [ISO/IEC 27005 — Risk Treatment Options](https://secureframe.com/blog/iso-27005)
- [Vulnerability Deduplication — Northstar.io](https://www.northstar.io/blog/vulnerability-deduplication/)
- [From Detection to Remediation: Root-Cause Remediation — Wiz](https://www.wiz.io/blog/from-detection-to-remediation-it-s-time-to-rethink-appsec-around-exploitability-a)
- [Risk Report vs. Risk Register — Project Management Academy](https://projectmanagementacademy.net/resources/blog/risk-report-vs-risk-register/)
