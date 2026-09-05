# Appendix C — Checklist for onboarding a new service onto observability

This list distills the sequence that proved sound across the whole book —
from the first line of instrumentation to the first alert and the first
runbook — into a form you can apply directly to the next service that needs
onboarding. It isn't meant to be followed linearly without thinking; as
Chapter 30 showed, reality will raise questions this list doesn't anticipate.
Use it as a starting point, not a contract.

## Phase 0 — Before a single line of code is written

- [ ] Does this service NATURALLY fit the existing instrumentation pattern
  (same language/runtime as services already onboarded), or does it need a
  new recipe? If it needs a new recipe — plan extra time for a pilot; don't
  assume the existing recipe will "just work."
- [ ] Assess this service's blast radius relative to the services already
  onboarded — this determines WHERE in the sequence it belongs (the rule
  from Chapter 30: the most critical part of the system goes LAST, as
  policy, not as an exception).
- [ ] Check whether the central gateway has capacity for a new sender
  WITHOUT degrading existing ones — if not, gateway autoscaling/capacity
  comes BEFORE fanning out to new services.

## Phase 1 — Basic instrumentation

- [ ] Automatic (zero-code) instrumentation for standard calls (HTTP/DB/
  message queue) enabled.
- [ ] Custom spans added for the BUSINESS context that automatic
  instrumentation can't see — did the job actually SUCCEED, not just exit
  with code 0?
- [ ] `service.name` and other resource attributes set explicitly — don't
  rely on the environment detector's default value.
- [ ] If the job is short-lived (scheduled/batch): a sidecar collector added
  to catch the final spans on shutdown, with a `stopTimeout` long enough
  for a graceful flush.

## Phase 2 — Verification before trusting anything

- [ ] Manually run one pass of the service and CONFIRM in the observability
  platform that all three signals (metrics, logs, spans) arrived — don't
  assume based on "the code looks right."
- [ ] Check whether any new attribute/label the service introduces has had
  its cardinality checked BEFORE production (Appendix A, Recipe #11) — not
  after.
- [ ] Check that the OTLP→Prometheus metric name translation isn't hiding
  the expected metric behind a CamelCase unit suffix (Appendix A, Recipe
  #10).

## Phase 3 — The first alert

- [ ] Define what "succeeded, but did nothing" means for THIS service — a
  joint condition (it ran, AND it produced no output), never either half
  alone.
- [ ] Define a coarse, exit-code alert AS A TEMPORARY MEASURE until the
  fine-grained mechanism is confirmed working — but plan to remove it as
  soon as the fine-grained mechanism has passed its soak period; don't
  leave both in place permanently.
- [ ] Assign an urgency level (critical/standard/silent) — an unfamiliar
  service defaults to standard (fail-safe), never silent by default.
- [ ] Check that the alert watching THIS service doesn't depend on the SAME
  infrastructure whose failure it's trying to catch (the
  watcher-outlives-the-watched principle).

## Phase 4 — The first runbook

- [ ] Write the runbook BEFORE the first real incident, not after — even a
  short, one-paragraph runbook beats an empty field at the moment an alert
  is already firing.
- [ ] The runbook must have a deep link directly to the relevant window in
  the observability platform — not a description like "open the dashboard
  and find the right panel."
- [ ] The runbook explicitly states WHEN to escalate further, not just what
  to try first.

## Phase 5 — Before the service is considered "done"

- [ ] Deliberately simulate at least one failure (if it's safe to do so)
  and check whether the alert ACTUALLY fires, not just whether it should
  fire by definition.
- [ ] Add the service to the explicit list of "instrumented" services that
  the alerting mechanism uses to decide how much detail to attach to a
  notification.
- [ ] Record the date and the version of the recipe used for onboarding —
  the next service may need a different recipe, and that difference should
  stay visible in hindsight.

## Phase 6 — Periodic review (not a one-time event)

- [ ] This service enters the next periodic program review (Chapter 31)
  just like any other — there's no such thing as "onboarded once, done
  forever."
- [ ] If this service's alert is ever silent longer than its expected
  activity period, that's a reason to investigate, not a reason for comfort
  (Appendix B — dead man's switch).
