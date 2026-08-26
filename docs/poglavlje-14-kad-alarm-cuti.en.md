# Chapter 14 — When the alert stays silent: gating, dedup, and the "silent gap"

A smoke detector in the kitchen is tuned to recognize one kind of danger
well: a sudden, dense concentration of smoke — something burning fast,
which the sensor catches within seconds. By its very nature, that same
detector is nearly blind to an entirely different kind of danger: a slow
carbon-monoxide leak that climbs hour by hour, never crossing the threshold
that would trigger a sudden reaction, and yet, given enough time, just as
dangerous. The detector isn't broken — it works exactly as designed. The
problem is that it was designed for one **shape** of danger, and the danger
that actually struck had an entirely different shape.

## 14.1 The question this chapter answers

An alert that is correctly defined, correctly deployed, and technically
works exactly as specified can, in practice, never reach a human being.
This chapter answers the question of how that happens, and through two
real case studies shows that this may be the most important, and
least written-about, topic in observability: **not the alert failing, but
its quiet, correct inactivity at exactly the moment it's needed most.**

## 14.2 How it was done — a practical walkthrough

### First case study: a mechanism designed for bursts, applied to a leak

The fleet of scheduled batch jobs has an anti-spam mechanism — if the same
job starts failing repeatedly, an alert isn't sent for every individual
failure, only once the number of failures crosses a threshold within a
short time window (three failures in thirty minutes). The idea behind this
is sound: a sudden burst of errors (say, ten failures in a minute from one
bad deploy) shouldn't flood the channel with ten identical messages.

The problem showed up with a job that failed **once per run**, on its
scheduled cadence, roughly once an hour. That pattern never satisfies the
"three in thirty minutes" threshold — not because the failure is rare, but
because it's **spread out**. The result: a mechanism designed to prevent
flooding the channel, applied to this pattern, became permanently,
structurally silent. Not a delay in alerting — a complete absence of
alerting, forever, no matter how many days in a row the job kept failing.

It was discovered by accident: someone noticed that the dashboard showed
failed job runs that had never arrived as a message in the channel. The
investigation showed that the anti-spam mechanism was working exactly as
specified — it recorded every failure, counted correctly, and correctly
decided the threshold hadn't been reached. The alert **existed**, was
**correctly defined**, and **still** never reached a human.

The deeper lesson from the investigation: the assumption "if we don't know
a job's category, default to treating it as if it needs an alert" had been
documented as a safety net — "unknown → default to noisy, not silent"
(deliberately written down as a principle). But that assumption was
written **before** the anti-spam mechanism was introduced, and nobody
re-read it after that change. Once the threshold was introduced, "default
to noisy" stopped meaning "we get notified" and started meaning "we get
notified only if it fails three times in thirty minutes" — a completely
different promise, under the same name.

### Second case study: two warnings that don't add up to an error

The same type of job, in a separate incident, was forcibly killed for
running out of memory **nineteen times over seventeen hours** — again
roughly once an hour, again spread out, again under the anti-spam
mechanism's threshold. The only message that reached the channel during
that period was a warning about **memory consumption** (not about the
failure) — "60% used, then 75%, then 90%" — at severity level **warning**,
not **error**.

The investigation uncovered something more subtle than plain silence:
**two separate warnings** were operating, both correctly, both at the same
time — one tracked memory usage and correctly signaled "dangerously high";
the other tracked failure frequency and correctly signaled "this job is
failing unusually often." Neither one, on its own, was wrong. But neither
of them, nor the two together, **added up** to the clear message "this job
is being killed for running out of memory, nineteen times, right now" — a
message that, by its actual content, clearly deserved severity **error**,
not two parallel **warning**s. The person reading the channel saw two
warnings and read them as "something low-priority is happening" — exactly
the wrong conclusion for what was actually happening.

It further emerged that the severity level of the memory warning itself
depended on the **sheer chance of measurement timing** — the system
samples memory usage roughly every twenty seconds, and whether that sample
lands above or below the critical threshold depends on exactly where in
time the sampling falls relative to the moment of the forced kill. The
same type of failure could, depending on sampling timing, produce either a
"warning" or a "critical" — the message's severity was a **gamble on
sampling timing**, not a property of what actually happened.

### What was fixed

The fix wasn't "lower the anti-spam mechanism's threshold" — that would
treat the symptom (too few messages) without treating the cause (the
mechanism can't distinguish the shape of the failure). Instead, an
explicit list of **failure reasons** was introduced that **bypass** the
anti-spam mechanism entirely — an out-of-memory failure is one such
reason, because it's deterministic and inherently prone to repeating,
unlike, say, a transient network stall, which deliberately **stays** under
the mechanism, because temporary silence really is the right response
there. The failure is still **recorded** without exception (the window
counter stays accurate) — only the decision about whether to **send**
changes for that category of reason.

Here is what the first case study looks like once measured — nineteen
failures spread across seventeen hours, each one individually under the
anti-spam mechanism's threshold, none of them ever sent:

![Nineteen failures spread across seventeen hours — each suppressed, none sent, because no pair of failures falls close enough together in time to satisfy the "three in thirty minutes" threshold.](diagrams/dashboard-suppression.png){: width="95%" }

## 14.3 Analytical section — why almost nobody else writes about this

### An anti-spam mechanism encodes an assumption about the shape of failure

It's worth naming what both case studies actually demonstrate: every
mechanism that suppresses repeated alerts implicitly assumes **how**
failures arrive — in bursts, rarely, in isolation, or spread out. "Three
in thirty minutes" is a reasonable threshold for a burst of errors from a
bad deploy. The same threshold, applied to a job that runs once an hour
and occasionally fails, is mathematically impossible to ever satisfy — not
because it's poorly tuned, but because it measures the wrong property for
that failure pattern. Before introducing any repeat-suppression mechanism,
it's worth explicitly enumerating which existing signals can **never**
satisfy the new threshold, no matter how long the failure persists — that's
the check that was skipped here, and it would have uncovered both case
studies in advance.

### The "two warnings" problem isn't about thresholds — it's about aggregating meaning

The second case study shows something the alerting literature rarely names
directly: a system can have **complete coverage** (every relevant signal
exists and correctly fires) and **still fail to convey an accurate
picture** to the person reading the result, because no single signal
carries the context that would explain that the other two signals are
**the same event**, seen from two angles. Coverage isn't the same as being
informed. When two independent, correct warnings describe the same real
situation, their sum doesn't automatically become "more serious" for the
reader — it stays "two low-priority signals," unless someone explicitly
designs the connection between them.

### The cost of none of this being noticed: a counterfactual scenario

It's worth playing out what would have happened had the anti-spam
mechanism never been reconsidered. A job failing once an hour would have
kept failing, forever, without a single message in the channel — not
because nobody would care, but because nobody would **know**. The
difference between "silent because everything is fine" and "silent
because the mechanism can't see this pattern" is invisible from the
outside — both look identical: an empty channel. That's exactly why this
gap was found by accident, by someone watching a dashboard, not by an
alert reporting itself.

Let's return to the smoke detector from the start of the chapter. It isn't
defective — it works exactly as calibrated. The problem arises when
someone assumes that one calibration is enough for every kind of danger it
needs to catch. **An alert that stays silent because the mechanism is
correctly operating on a wrong assumption is more dangerous than an alert
that's simply broken — because a broken alert at least looks suspicious,
while correct-but-wrongly-calibrated looks like calm.**

## 14.4 Rules collected from this chapter

- Before introducing any mechanism that suppresses repeated alerts,
  explicitly check which existing, legitimate failure pattern can
  **never** satisfy the new threshold, no matter how long it persists.
- Distinguish failure reasons by nature (deterministic and prone to
  repeating versus transient and self-healing), and let the first category
  bypass the repeat-suppression mechanism entirely.
- Never change **whether a failure is recorded** in order to change
  **whether a message about it is sent** — the counter must stay accurate
  independent of the notification decision, otherwise the next failure
  gets misread as isolated.
- Ask whether two or more separate, correct warnings might describe the
  **same** real event — if they might, add an explicit link that tells the
  reader so, instead of relying on them to add it up themselves.
- Whenever you introduce a mechanism that suppresses something, measure
  its effect immediately after introducing it (how many messages
  disappeared, and for which families) — don't assume a drop in message
  count means "the system got healthier."

## 14.5 Exercise for the reader

Find any mechanism in your system that suppresses repeated alerts (dedup,
rate-limit, repeat-count threshold). Imagine a failure that happens
exactly once per every scheduled run, forever — would that mechanism ever
let a message through? If not, that's your candidate for a "silent gap"
waiting for someone to notice it by accident on a dashboard, instead of
the system reporting it itself.

---

### Sources used in the analytical section

- [How to Implement Alert Routing — OneUptime](https://oneuptime.com/blog/post/2026-01-30-alert-routing/view)
- [Alerting best practices — Grafana documentation](https://grafana.com/docs/grafana/latest/alerting/guides/best-practices/)
- [Stop drowning in alerts: DevOps alert management strategies — Hyperping](https://hyperping.com/blog/devops-alert-management)
- [Mastering incident routing — incident.io](https://incident.io/blog/mastering-incident-routing-a-critical-component-in-incident-management)
