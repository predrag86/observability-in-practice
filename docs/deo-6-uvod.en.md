# Part VI — Governance, compliance, and maturity

## Before we start: once the system works, the questions change

Every previous part of the book has, at its core, answered one question:
does the system see what it needs to see, and does the team react in time
when something goes wrong. Part VI assumes that question is already
settled, and asks five entirely different ones:

- **Chapter 25** asks whether telemetry, while doing its job, leaks
  information it shouldn't be carrying — privacy as a known leak pattern
  with a precise name, not an abstract worry.
- **Chapter 26** asks whether the observability system can be used as
  evidence in front of an external auditor — observability as a
  compliance control, on the concrete example of SOC 2.
- **Chapter 27** asks how, when cost, performance, reliability, and
  security are all equally legitimate, you even choose what to work on
  next.
- **Chapter 28** asks what changes when the first reader of telemetry
  after an incident is no longer a human, but an AI agent — and where
  the boundary lies on what that agent can actually know.
- **Chapter 29** asks what happens when two configurations that should
  be identical quietly go their separate ways — and whether that
  incident gets quietly patched, or used as the reason to change the
  process that produced it.

The common thread: these are organizational and trust questions, not the
technical implementation questions that carried the previous parts. A
system that works correctly on a technical level, but can't answer any
of these five questions, isn't a mature system — it's just a system that
hasn't been tested the right way yet. Part VII, which closes the book,
takes that exact measure of maturity and asks what it looks like applied
to the book's own, real, multi-month rollout.
