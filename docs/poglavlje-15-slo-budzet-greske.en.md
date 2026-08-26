# Chapter 15 — SLOs and error-budget-based alerts

A car's fuel gauge doesn't distinguish between two entirely different
scenarios that look identical on the dial: fuel leaking out through a large
hole in the tank and draining the whole tank within an hour, and fuel being
consumed at a normal, slow rate that lasts a week. Both scenarios eventually
light up the same "low fuel" warning. But the urgency of the response is
completely different — one is a reason to pull over immediately, the other
is a reason to stop by the gas station tomorrow. A gauge that only looks at
the **current level** can't see that difference; only someone watching the
**rate** at which the level is dropping can see it.

## 15.1 The question this chapter answers

A threshold based on a current value ("error rate is above 1%") doesn't
distinguish a sudden, serious degradation from a mild, chronic leak that
would consume the same error budget over the course of a month. This
chapter answers the question of how to build an alert that
**distinguishes** between those two scenarios — and, through a real case
study, shows what happens when the input signal for that alert isn't,
itself, what it claims to be.

## 15.2 How it was done — a practical overview

### Multi-window burn-rate alerts — the basic mechanics

An SLO (service-level objective) defines what percentage of requests are
allowed to "miss" within a defined period while the service still counts
as "good enough" — for instance, 99.9% monthly availability means a budget
of 0.1% failed requests. **Burn rate** is the speed at which that budget
is being consumed relative to a normal, sustainable pace: a burn rate of
1× means "we're spending the budget at exactly the rate that would
exhaust it by the end of the period, no faster and no slower"; a burn rate
of 10× means "we're spending it ten times faster — at this rate, the
budget would run out in a tenth of the period."

The implementation this book follows uses **three tiers** of burn-rate
alert, each with **two time windows** at once — a long window that
measures whether the budget has actually been significantly consumed, and
a short window that confirms the consumption is happening **right now**,
not that it happened and then stopped:

- **Fast burn** (page, urgent): long window 1 hour, short window 5
  minutes, burn rate 14.4× — a serious, ongoing problem that deserves
  immediate attention.
- **Medium burn** (page): long window 6 hours, short window 30 minutes,
  burn rate 6×.
- **Slow burn** (ticket, not urgent): long window 3 days, short window 6
  hours, burn rate 1× — a chronic leak that deserves attention, but
  doesn't wake anyone in the middle of the night.

The two windows work together deliberately: the long window alone would,
once the problem is fixed, keep showing an elevated burn rate for hours
after the actual recovery (because a 6-hour window "remembers" the error
from the previous hour), producing an alert that's as slow to clear as it
was to fire. The short window fixes that — the alert clears as soon as
the short window shows that budget consumption is no longer active, even
while the long window still "remembers" the earlier consumption.

### Case study: when the SLI itself is lying

In the implementation this book follows, these alerts started firing
repeatedly — the medium and slow tiers, multiple times a day. The first
assumption would be that the service was genuinely degrading. **The
service was completely healthy.** The authoritative signal (the count of
actual failed responses measured at the load balancer level, outside the
application itself) showed only **seven** failed requests over
twenty-four hours — practically 100% availability. The SLI itself (the
signal the alert was based on), derived from a histogram inside the
application, claimed something entirely different: over a million
"failed" requests on a single endpoint, and over sixteen million total
requests to that same endpoint in the same period — a traffic rate that
was physically impossible for that number of instances.

**The cause:** the service auto-scales horizontally, adding and removing
instances throughout the day according to traffic patterns. Each instance
carries its own identifier in its histogram series. A query that sums
"increase" over a time window, applied across **all** series at once,
extrapolates each individual series to the edges of the window — and when
dozens of short-lived instances appear and disappear over the course of a
day, that sum of extrapolations **massively overestimates** the real
count. The signature of the bug was unambiguous right in the data: the
error count per half-hour interval was identical, down to the last digit,
for **twelve consecutive intervals in a row** — real traffic never
produces an identical count twelve times in a row; that's an artifact of
extrapolation, not a measurement.

### How the team responded — discipline, not reflex

The first reaction **was not** to lower the alert threshold to make it
stop firing — that would have hidden the symptom without understanding
the cause, and left a broken signal alive and undetected. Instead: the
rule was **paused** explicitly (it stays visible in the configuration as
paused, not deleted, and not silently unnoticed), the real error count
was verified against an independent, authoritative source (the load
balancer, not the application's own histogram), and only then was it
decided how to proceed: the SLI needed to be **rebuilt** on a signal
resistant to fluctuations in instance count — either by using that same
authoritative external counter as the source, or by aggregating the
histogram on a stable label before computing, instead of on the unstable
instance identifier.

Here's what the mechanics of the two windows together look like during a
short-lived incident — the short window spikes instantly and drops
instantly, the long window rises more slowly and slowly "comes back
down," which is why the alert clears quickly after a real recovery
instead of lagging behind for hours:

![The short window (5 min) reacts instantly and clears instantly; the long window (1 h) rises more slowly and falls more slowly — the combination delivers both fast detection and fast alert clearing.](diagrams/dashboard-burnrate.png){: width="95%" }

## 15.3 Analytical section — why multi-window isn't an arbitrary complication

### The official recommendation: why a single threshold is never enough

Official SRE practice explicitly explains why a simple single-window
threshold can't simultaneously achieve good precision, good recall, fast
detection, **and** fast alert clearing. A one-hour window detects a
serious outage quickly, but keeps firing for an hour after the actual
recovery — which confuses people and erodes trust in the alert. The
solution isn't one "correct" window, but a **pair** of windows per
urgency tier, with the short window's recommended length at roughly
one-twelfth of the long window — short enough to confirm that budget
consumption is **currently** active, long enough not to react to a few
seconds of noise.

### The implementation follows the recipe, with one specific addition

The three tiers (fast/medium/slow) and their thresholds follow the
official pattern almost literally — this is, similarly to Chapter 10, a
case where there's no need for an invented story of deviation. What the
recipe rarely covers explicitly is **the question of the SLI's own
reliability** — the recipe assumes that counting the success/failure
signal is reliable, and focuses on how to react to changes in that count.
The implementation this book follows, through its own experience, added a
step the recipe doesn't spell out: **before trusting any threshold, check
whether the absolute numbers behind the ratio make sense at all** —
sixteen million requests to a single endpoint in a day is a number that
anyone familiar with the system's capacity would recognize as impossible,
had someone looked at it before believing the derived percentage.

### The cost of a first reaction that lowers the threshold: a counterfactual scenario

It's worth playing out the alternative concretely. Had the team, instead
of pausing the rule and investigating the cause, simply raised the
threshold to make the alert stop firing (say, doubled the burn-rate
cutoff), the result would have looked like a solved problem — the channel
would have gone quiet. But the actual, broken SLI would have stayed
untouched, and the system would have lost the ability to detect **real**
degradation of that same service, because the threshold would now be
tuned to tolerate false noise instead of measuring the real state. This
is the same pattern already seen in Chapter 11, with cardinality
reduction applied in the wrong place: a measure that looks like a fix but
actually removes the ability to notice the problem at all the next time
it genuinely happens.

Let's return to the fuel gauge from the start of the chapter. The "low
fuel" light on its own says nothing about urgency — you need to know the
**rate** of the drop to know whether to stop immediately or swing by the
pump tomorrow. But even the best rate-of-drop gauge is useless if the
fuel-level sensor itself is broken and reporting impossible numbers.
**A burn-rate alert solves the question of urgency — but it only solves
it once someone has verified that the signal being measured actually
measures what it claims to measure.**

## 15.4 Rules collected from this chapter

- Use multi-window burn-rate alerts instead of a single threshold on a
  single window — a pair of long and short windows solves both fast
  detection and fast clearing, which no single window can do on its own.
- Set the short window to roughly one-twelfth of the long window — short
  enough to confirm current budget consumption, long enough not to react
  to noise.
- Before you trust a derived percentage or ratio, check the absolute
  numbers behind it against an independent, authoritative source — a
  ratio can look plausible while both of its terms are nonsensical.
- When an alert starts firing unexpectedly often, the first reaction
  isn't lowering its sensitivity — the first reaction is checking whether
  the signal the alert is based on actually measures what it claims to
  measure.
- Avoid rate/increase queries across high-churn labels (an instance
  identifier that keeps changing) in an SLI — aggregate them onto a
  stable label before computing, or use a recording rule that's resistant
  to that churn.

## 15.5 Exercise for the reader

Find an SLO alert in your own system and check: does it have only one
window, or a pair (long + short)? Then take the absolute numbers behind
its current ratio (numerator and denominator, not just the percentage)
and compare them against an independent source, if one exists. Do they
agree? If you don't have an independent source to compare against — that
is the gap this chapter is asking you to notice, before your alert one
day tells you something that isn't true.

---

### Sources used in the analytical section

- [Alerting on SLOs — Google SRE Workbook](https://sre.google/workbook/alerting-on-slos/)
- [How to Build Burn Rate Alerts — OneUptime](https://oneuptime.com/blog/post/2026-01-30-sre-burn-rate-alerts/view)
- [How to implement multi-window, multi-burn-rate alerts with Grafana Cloud — Grafana Labs](https://grafana.com/blog/how-to-implement-multi-window-multi-burn-rate-alerts-with-grafana-cloud/)
- [The Multi-Window Multi-Burn-Rate Alert — Nova AI Ops Blog](https://novaaiops.com/blog/the-multi-window-multi-burn-rate-alert)
