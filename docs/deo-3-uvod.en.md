# Part III — Processing, cardinality, and cost

## Before we start: the same problem, three different angles

Part II answered how telemetry is collected from every layer of the
system — the gateway, instrumentation, the sidecar, pull-based patterns,
RUM, synthetic monitoring. This part picks up exactly where Part II left
off: the collector already holds the signal in hand, before any of it
goes to the cloud and starts costing money. The three chapters that
follow aren't three separate pieces of advice — they're **the same
problem** (controlling cost without losing signal) seen from three
different angles:

- **Chapter 10** asks whether the order of processing inside the
  pipeline matters at all, or whether it's just a stylistic choice — and
  shows why the wrong order can make the signal more expensive or poorer
  before anyone notices.
- **Chapter 11** takes a broader view: how cardinality — the number of
  unique label combinations — naturally grows past budget, quietly and
  gradually, until one day a bill arrives that surprises everyone even
  though it had been growing for months.
- **Chapter 12** brings the same question down to one concrete signal —
  traces — and compares two opposite places where the sampling decision
  can be made: at the server, where the whole trace is visible before the
  decision, or at the collector, where the decision is made with only
  part of the picture.

The common thread through all three chapters: the cost of telemetry
isn't a fixed expense accepted once — it's a variable that pipeline
architecture, label growth patterns, and sampling strategy together
either keep under control, or don't. Part IV, which follows, assumes
that control has already been established, and moves on to what happens
when a processed, cheap signal needs to wake up a human.
