# Chapter 17 — Postmortem culture

A commission investigating a maritime accident doesn't write its report to
establish whose fault it was. It writes it to establish **why** the system —
the ship, the crew, the procedures, the equipment — allowed the accident to
happen, and exactly what needs to change so that the next ship, the next
crew, in a similar situation, doesn't end up the same way. The captain who
was on the bridge that night is named in the report — but named as a
participant in a chain of decisions, not as a target. A report that instead
went looking for someone to blame would teach the crew exactly one thing:
next time, don't report the mistake while there's still time to fix it. That
is precisely what the report the commission writes is meant to prevent.

## 17.1 The question this chapter answers

Something shipped, and then it broke in a way that cost someone time or
trust. Who writes what about it, why, and who is that document actually
for? This chapter answers that question through the convention used in the
implementation this book follows — and through a pattern that, once you look
at the whole index of postmortems written, repeats itself surprisingly
often: **a missing alert is a more common source of pain than a system
falling over.**

## 17.2 How it's done — a practical overview

### The blameless convention

The postmortem in the implementation this book follows starts from a single
assumption, written down explicitly as a rule: everyone involved in an
incident had good intentions and did the best they could with the
information they had at that moment. The document's target is the system
and the process, not a person. This assumption isn't a cosmetic courtesy —
it's a functional precondition: a team that knows a mistake will be sought
out and named **hides** problems instead of reporting them, and a hidden
problem doesn't get fixed, it just waits for the next time it will cost
more.

### When a postmortem gets written

It isn't written for every mistake. It's written when something has been
**shipped** and then broke in a way that cost someone time or trust —
user-visible downtime, data loss, an on-call intervention outside the usual
flow (a rollback, manually rerouting traffic), or a period where monitoring
missed something a human had to discover by hand. A bug caught in code
review or a local test doesn't need a postmortem — it never reached real
cost. Any participant in the system can request that a postmortem be
written for any event, independent of the formal criteria — the criteria
exist to prevent a "does this deserve a document" debate, not to limit who
is allowed to ask.

### A skimmable summary, and indexing

Every postmortem opens with a frame meant to be read in ten seconds:
severity, what exactly broke, the scope of impact, current status. The
details — timeline, root cause, investigation, fixes, lessons learned —
follow below, but the frame at the top has to be sufficient on its own for
someone just scanning the index to know whether they need to open the full
document. Every postmortem is added to a central index, with a date, a
short description, and a status — not because anyone will read it right
away, but because someone will **search** for it months later, when a
similar pattern shows up and someone suspects "haven't we seen this
before."

### The pattern the index reveals

Look at the whole index of postmortems written in the implementation this
book follows, and one pattern repeats itself surprisingly often: incidents
where **nothing fell over**, where there was no service interruption or
data loss, and yet a postmortem was justly written — because an alert that
should have existed, quietly, correctly by its own logic, never reached a
human being. One such case: an investigation into a single missed alert
found that the mechanism for tracking alert coverage was a manually
maintained list that was never automatically reconciled against the actual
state of the fleet — which, looking back, had opened six separate,
independent gaps in coverage over seven weeks, none of them noticed until
someone happened to spot a discrepancy on a dashboard. A second, related
case happened a day later, on the same type of job, but through an entirely
different mechanism: two separate, individually correct low-severity
warnings that never added up into a clear picture that something serious
was recurring. Neither of these two incidents took down a single service.
Both were, by the written postmortem's own admission, more damaging to
trust in the system than some actual, short-lived outage.

![A postmortem looks backward; from it you distill a runbook (forward-looking, for next time) or a handoff (a one-time request handed to a single owner) — three documents, three different directions.](diagrams/ch17-tri-tipa.png){: width="90%" }

### The extreme case of the pattern: four hundred sixty-nine days of silence

It's worth naming one specific entry from the index as the extreme
endpoint of the pattern described above — not because it's typical, but
because it shows how far a "missing alert" can go before anyone notices. A
scheduled job failed **every single time it ran, without exception, for
four hundred sixty-nine days straight**. The alert meant to report that
failure wasn't missing — it was present, enabled, and correctly wired. The
problem lay in the nature of the notification mechanism itself: the
system sends a message on a state **change**, not for as long as a state
persists. The alert transitioned once, on the very day the failures began,
from "OK" to "firing," and on that occasion sent exactly one notification.
Since the state never returned to "OK" afterward (the job never
succeeded), there was no further state change to trigger a second
message — not one, the whole time.

It was discovered entirely by accident, not through a search or a
dashboard: someone was checking whether an old version of a tool could
safely be removed as "probably dead code," and noticed that the call count
for that job wasn't zero at all, when it should have been, under the
assumption that nobody used that code anymore. The postmortem written
about this finding didn't stop at "let's fix this one alert" — it
triggered a broader push: a review of the entire fleet of similar jobs
uncovered five more that were failing with no alert at all, and that most
jobs in that category had no notification mechanism that would survive
exactly this pattern (persists-but-doesn't-change). A postmortem that
finds one case and asks "where else is this hiding" is worth far more than
one that closes just that one, named case.

### The same alert, three unrelated causes — the danger of the first explanation that fits

One family of jobs triggered an alert **seventy times** in a month, every
time in the same shape, every time at the highest severity level, with no
mechanism at all for merging repeated messages — seventy separate calls
into the channel. The first, entirely reasonable assumption was that a
single cause was repeating. An investigation that stopped at the first
explanation that fit a handful of examples would easily have missed it:
when the postmortem systematically broke down all seventy calls instead of
sampling a few of them, it turned out that **three** completely unrelated
causes stood behind the identical alert shape — one data-processing bug
affecting about nine out of ten cases, a separate, rarer class of failure
at the database network-connection level, and one call that didn't belong
to this job family at all but to a neighboring one, from an external
platform that pulls stale jobs out of rotation — a coincidental overlap in
timing that nearly sent the investigation down the wrong track.

Had the investigation stopped after the first two or three cases
reviewed, it would likely have concluded there was one dominant cause and
proposed a single fix — technically correct for most cases, but blind to
the remaining tenth and to the completely misattributed call that didn't
even belong to this family. The lesson isn't specific to this job family:
when the same alert shape comes often enough to become a serious cost,
it's worth breaking down the **entire** population of calls, not just
enough of them to confirm the first plausible explanation — an identical
external alert shape guarantees neither one shared cause behind it, nor
that every occurrence is fully related.

![The alert correctly transitions into the firing state and sends exactly one notification on the day of the failure — the system only notifies on a state change, so 469 days of continuous, unchanged failure afterward send no further message. Discovered by accident, during an unrelated task.](diagrams/ch17-469-dana.png){: width="85%" }

## 17.3 Analytical section — why "no one's at fault" is harder than it sounds

### The official recommendation: blameless as a functional requirement, not courtesy

Official SRE practice states this directly: you can't "fix" people, but you
can fix systems and processes. The approach is borrowed from healthcare and
aviation, two industries where the consequence of hiding a mistake is far
greater than the consequence of admitting one — and in both, a culture that
goes looking for someone to blame consistently produces less reporting, not
fewer mistakes. The same practice lists concrete triggers for writing a
postmortem (user-visible downtime, data loss, a manual on-call
intervention, resolution time above a defined threshold, a monitoring
failure that required manual discovery) — an almost identical list to the
one used here.

### Sustaining the culture is harder than writing one good document

Material on sustaining the postmortem practice points out that the biggest
risk is the gradual erosion of discipline, not a single bad postmortem —
visibility and acknowledgment from leadership, a centralized index that
makes it possible to search for patterns over time, and regular feedback on
whether the process is a burden or a help to the team are all listed as
necessary for the practice to survive past the initial enthusiasm. This is
why indexing here isn't a minor administrative detail — the index is what
makes it possible for a pattern like "the missing alert" to be noticed as a
**pattern** at all, rather than as a string of unconnected incidents.

### The cost of a blame-seeking culture: a counterfactual scenario

It's worth playing out the alternative concretely. Had both incidents about
missed alerts resulted in the question "who forgot to add that job to the
list" instead of "why was the list maintained by hand at all," the outcome
would probably have been identical as far as fixing that one specific gap
— but the systemic mechanism (the lack of an automatic check against the
actual state of the fleet) would have stayed untouched, waiting for the
next manual mistake of the same kind. Worse still: the next engineer who
noticed a similar gap would have had a reason to quietly fix it themselves,
without reporting it, to avoid being the next one named — which would make
exactly the pattern this postmortem uncovered (gaps accumulating unnoticed)
**more** likely, not less.

Return to the maritime accident commission from the start of the chapter.
Its report names the captain, but names him as a participant in the chain
of decisions that led to the accident — not as the culprit whose removal
is, on its own, the fix. The next ship doesn't become safer because one
captain was punished; it becomes safer because procedures, equipment, or
training were changed based on what the report uncovered. **A postmortem
that looks for someone to blame resolves one incident. A postmortem that
looks for the system prevents the next one.**

## 17.4 Rules collected from this chapter

- Write a postmortem when something has shipped and then broke in a way
  that cost someone time or trust — not for every mistake, but for every
  one that reached real cost.
- Keep the summary at the top skimmable in ten seconds — severity, what
  broke, scope, status — because most readers of the index will never open
  the full document.
- Index every postmortem centrally, with a searchable description — the
  index's value isn't at the moment it's written, it's months later, when
  someone needs to check whether a similar pattern has already been seen.
- Write a postmortem even for incidents where nothing fell over, if an
  alert that should have existed stayed silent — the absence of a signal
  is just as worthwhile a subject as a system falling over, often more so.
- Cultivate a blameless culture actively, not as a one-time statement of
  principle — visibility from leadership, regular checks on whether the
  process is a burden on the team, and an index someone actually uses are
  all necessary for the practice to survive past the initial enthusiasm.
- When a postmortem uncovers one case of a missed alert, expand the
  investigation to the entire related fleet before declaring the problem
  closed — one finding is rarely the only instance.
- When the same alert shape comes often enough to become a serious cost,
  break down the entire population of calls before accepting the first
  plausible explanation — an identical shape doesn't guarantee one shared
  cause.

## 17.5 Exercise for the reader

Find the most recent incident on your team where something was missed —
not a system falling over, but a missed signal, a missed alert, a missed
check. Is there a written record of it, searchable, with a clear
description of what was systemically changed so it doesn't happen again?
If there isn't, that's the gap this chapter is asking you to close — not
because that particular miss was catastrophic, but because the next time
it repeats is far more expensive if no one knows it already happened once.

---

### Sources used in the analytical section

- [Postmortem Culture: Learning from Failure — Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Postmortem Practices for Incident Management — Google SRE Workbook](https://sre.google/workbook/postmortem-culture/)
- [How to run a blameless postmortem — Atlassian](https://www.atlassian.com/incident-management/postmortem/blameless)
- [How to Run Effective Blameless Postmortems — Rootly](https://rootly.com/incident-postmortems/blameless)
