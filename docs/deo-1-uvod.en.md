# Part I — Fundamentals

## Before we start: three decisions you only make once

The book's introduction has already set the scene — which system the book
follows, where the material comes from, how every chapter is structured.
Part I is where that story stops being just context and becomes
**vocabulary**: three chapters, three decisions that in a real
implementation get made exactly once, right at the start, and after that
everything else in the book quietly assumes they've already been settled.

The order isn't arbitrary:

- **Chapter 1** asks the question that comes before any tool: what does
  "observability" actually mean once it's distinguished from the monitoring
  that existed before that name — and why that distinction isn't cosmetic,
  but changes what gets built first.
- **Chapter 2** introduces OpenTelemetry not as a library to install, but as
  a mental model — a shared language in which every part of the system,
  regardless of who wrote it, describes what it measures. Without this
  chapter, Chapter 3 has nothing to decide between.
- **Chapter 3** is the first time the book stands on ground that's purely
  business, not technical: where telemetry physically lives, who operates
  it, and at what price — a question that has to come last in this part,
  because comparing platforms can't be done meaningfully until you know
  what's actually being sent (Chapter 2) and why it's worth measuring at all
  (Chapter 1).

This pattern — concept first, then protocol, then platform — is worth
remembering, because the book never comes back to it explicitly, but every
part that follows quietly relies on it. Part II, which comes next, doesn't
re-ask "what is observability" or "why OpenTelemetry" — it assumes both
questions are already behind us, and moves straight into how the signal is
actually collected from every layer of the system.
