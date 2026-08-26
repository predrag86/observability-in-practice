# Part IV — Alerting, SLOs, and incident response

## Before we start: one incident, told across five chapters

Unlike the other parts of the book, each of which covers one layer or one
mechanism independently, Part IV follows **one continuous path** — from
the moment something goes wrong to the moment the team has extracted a
lesson from it — across five chapters, in the order that path actually
unfolds:

- **Chapter 13** lays out the architecture: two completely different
  paths by which a signal about a problem arrives — one automatic, one
  human — which ultimately converge on the same destination channel.
- **Chapter 14** covers the opposite case: what happens when an alert
  that should have fired reports nothing — gating, dedup, and the
  "silent gap" that forms exactly where it's hardest to notice.
- **Chapter 15** introduces SLOs and error-budget-based alerts — a way to
  gauge how urgently to react based on how fast the budget is being
  consumed, not just whether a threshold has been crossed.
- **Chapter 16** moves to the moment a human has already been paged: the
  runbook as the bridge between an alert and a concrete fix, structured
  to work under pressure, not just on paper.
- **Chapter 17** closes the loop: postmortem culture that turns an
  incident into a lesson for the system, not a hunt for someone to blame.

These five chapters can be read as one story, from the first signal to
the last line written in the postmortem document. Part V, which follows,
assumes this path — from signal to resolution — already exists and
works, and applies it in turn to every individual layer of the system.
