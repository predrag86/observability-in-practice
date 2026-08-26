# Appendix D — Runbook template and postmortem template

Two templates, ready to copy. The difference between them is the difference
that runs through the whole book: a runbook looks FORWARD ("next time this
fires, do this") and is written BEFORE an incident; a postmortem looks
BACKWARD ("this happened, here's why") and is written AFTER. A runbook is
often distilled FROM a postmortem, but they're two separate documents with
two separate readers at two separate moments.

## D.1 — Runbook template

```markdown
# Runbook — <Failure class, not a single event>

> **Alert that triggers this:** <alert rule name/number>
> **Channel:** <where the notification arrives>
> **Last reviewed:** <YYYY-MM-DD> · **Owner:** <name/team>

## When this is used

<One or two sentences — exactly which alert/symptom leads
here, and what this does NOT cover (point to the neighboring
runbook if the symptoms look similar).>

## First check — before anything else

<One or two questions that immediately narrow the space of
possible causes. Example pattern: "is this a routine
scale-down shutdown (exit=143) or an actual failure?" —
distinguishing benign from real is always the first step.>

## Decision tree

1. <Question #1> → if YES, go to <action/link>; if NO, continue.
2. <Question #2> → ...
3. <Question #3> → ...

## Deep links

- <A direct link to a dashboard/query pre-set to the
  relevant time window and filter — not a description of how
  to get there manually.>

## Known pitfalls

- <Something that resembles this failure but isn't — and how
  to tell them apart.>

## When to escalate

<An explicit condition after which this runbook is abandoned
and someone else is called — a time threshold, or "if step 3
doesn't help".>

## Related

- Postmortem(s) this runbook was distilled from: <link(s)>
```

## D.2 — Postmortem template

```markdown
# <Title — what broke, in plain language>

> **Severity:** <Low / Medium / High / Critical>
> **Detected:** <YYYY-MM-DD HH:MM>
> **Resolved:** <YYYY-MM-DD HH:MM>
> **Blast radius:** <who/what was affected>
> **Status:** <RESOLVED / MITIGATED / OPEN>
> **Author:** <name>

## Summary

<2-4 sentences. What happened, the symptom visible to the
user, and the cause, in one sentence. Someone should be able
to understand the whole incident from this paragraph alone.>

## Impact

<Concrete: who was affected, what they couldn't do or were
misled into believing, for how long. Also write down what was
NOT affected — explicitly bound the blast radius.>

## Timeline

All times in <timezone>.

| Time | Event |
| --- | --- |
| <when the cause was introduced> | <the commit that planted the bug> |
| <when it was detected> | <how it surfaced> |
| ... | ... |
| <when it was resolved> | <fix live + confirmed> |

## Root cause

<The actual mechanism. Be precise — quote code,
configuration, the exact wrong value. Explain WHY it produced
that specific symptom, not just what was wrong.>

## Detection

<How was it detected? Who noticed, through which signal? Was
the observability system silent — and should it have been?>

## Resolution

<The fix. What was changed, how it was verified, how it was
shipped to production.>

## Why it wasn't caught earlier

<The honest part. Which check/test/guardrail would have
caught this, and didn't exist or wasn't run.>

## Lessons learned

- <What we know now.>

## Action items

| # | Action | Owner | Status |
| - | --- | --- | --- |
| 1 | <follow-up> | <who> | <in progress/done> |
```

## D.3 — A note on the discipline of filling these in

Both templates are only worth as much as they're filled in consistently — an
empty "Why it wasn't caught earlier" field is a common sign that the
postmortem was written to be closed, not to be learned from. The same goes
for a runbook whose "Known pitfalls" field stays empty after the first use —
the first real application of a runbook almost always turns up at least one
pitfall the original didn't anticipate; go back and add it.
