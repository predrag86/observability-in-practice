# Chapter 2 — OpenTelemetry: a mental model before the first line of code

Before the standardized shipping container, freight transport was a
combinatorial nightmare. Every port had its own loading equipment, every
ship its own hold layout, every type of cargo its own packaging tailored to
that specific route. Moving cargo from a ship to a train, then to a truck,
meant someone physically repacking the goods at every handoff point — slow,
expensive, and full of opportunities for something to be lost or damaged at
the boundary between two systems.

The 1956 container didn't solve the problem by inventing a better way to
pack goods. It solved the problem by standardizing the **boundary**: exact
dimensions, exact attachment points, an exact way the container gets lifted
and set down. What's *inside* — tea, machine parts, textiles — becomes
completely irrelevant to the ship, the crane, and the train. They don't know
or care about the contents; they only know the shape of the boundary.

OpenTelemetry does the same thing for telemetry. It doesn't dictate how an
application should be written, and it doesn't insist on one language or
framework. It only dictates **the shape of the boundary**: the format in
which telemetry data travels (OTLP), and the vocabulary of names used to
describe that boundary (semantic conventions) — so that the collector, the
gateway, and the cloud platform on the other side can all work with the
data without ever needing to know what language the application producing
it was written in.

## 2.1 The question this chapter answers

Before writing the first line of instrumentation for any specific
application, you have to answer a question that determines everything that
follows: **what exactly does OpenTelemetry standardize, and what does it
deliberately leave open for every language and every team to solve in its
own way?**

This question isn't academic. The answer directly explains why the same
organization, within the same system, quite legitimately instruments its
Java services one way and its Python services in a visibly different way —
and why that's *not* inconsistency, but exactly the amount of freedom
OpenTelemetry deliberately allows above the shared boundary everyone has to
respect.

## 2.2 How it was actually done — a practical walkthrough

In the implementation this book follows, two languages dominate the
application portfolio — Java and Python — and instrumentation was done in
two visibly different ways, by a deliberate decision, not by accident.

**Java services** use an **auto-instrumentation agent**
(`opentelemetry-javaagent.jar`) attached to the JVM via the `-javaagent`
flag at startup, without a single change to the application's source code.
At runtime, the agent recognizes known libraries (HTTP clients, JDBC
drivers, well-known frameworks) and automatically injects instrumentation
into them through bytecode manipulation. For a team maintaining dozens of
Java services, this was the deciding argument: a new application gets
traces, metrics, and context propagation on day one, without a single line
of code dedicated to observability, and without the risk of someone
forgetting to add it.

**Python services** take a different path — an **SDK distribution with an
entrypoint shim**. There's no equivalent here of a Java agent that would be
equally reliable across the whole Python ecosystem (Python's
auto-instrumentation works through monkey-patching known libraries at
process startup, which is structurally more fragile than the JVM's
bytecode-manipulation approach, and more sensitive to library versions).
Rather than relying on that fragility, every Python service has an
explicit, small initialization point — an entrypoint shim — that runs before
the application's main code, manually sets up the OpenTelemetry SDK,
providers, and exporters, and only then hands control to the application.
Instrumentation is still mostly automatic for known libraries (through the
`opentelemetry-instrument` layer), but the *initialization* is explicit and
visible in the repository, instead of hidden in a startup flag.

What stays **exactly the same** for both languages — and this is the heart
of this chapter — is:

- The format both types of services use to send data onward is **OTLP**
  (OpenTelemetry Protocol) over HTTP, to the same gateway from Chapter 4.
- The attribute names both languages use for the same concepts (HTTP
  method, status code, database name, service name) come from the **same
  vocabulary** — semantic conventions — so that a query in Grafana Cloud
  filtering on `http.response.status_code` works identically over data from
  both Java and Python services, with no per-language special-casing.
- Both types of services set the same minimal set of resource attributes at
  startup (service name, version, environment, instance) — an agreement
  independent of language, laid out in the shared internal convention
  covered in Chapter 6.

In other words: **how** telemetry is produced differs by language, for
reasons that language imposes. **What** telemetry means, once it reaches the
gateway, is identical regardless of where it came from. That's exactly the
line at which this chapter's opening container analogy separates "what's
inside" from "what the boundary looks like."

## 2.3 Analytical section — why OTLP had to exist at all, and what "semantic conventions" actually mean

### The problem OpenTelemetry solved wasn't a lack of tools, but their incompatibility

Before OpenTelemetry (born from the 2019 merger of two earlier projects,
OpenTracing and OpenCensus), an organization that wanted metrics, logs, and
traces chose a separate format and a separate SDK for each, often per
vendor: the Zipkin format for traces, StatsD for metrics, a proprietary log
format for logs, each with its own client libraries per language. When an
organization wanted to switch observability vendors, it had to change
instrumentation in every application — because the **data format itself**
was tied to the vendor, not just the destination it was sent to.

OTLP solves that problem the same way the standard shipping container solves
the transport problem: it defines one protocol (Protocol Buffers over gRPC
or HTTP) with a clearly defined schema for all three signal types,
independent of any specific vendor. The application speaks OTLP; the
collector and gateway translate OTLP into whatever the specific cloud
platform expects on its end. This is why switching vendors in the system
this book follows (had that ever happened) would be the gateway layer's job
from Chapter 4, not any individual application's job — exactly the way
changing which port a ship docks at doesn't require the cargo inside the
container to be repacked.

### Semantic conventions: a vocabulary, not an implementation

Semantic conventions are, per the official OpenTelemetry documentation, an
agreed-upon set of names and types for attributes that describe common
concepts — an HTTP request, a database, a messaging system, a resource
generating telemetry. The goal isn't to dictate *how* telemetry is
generated (that remains the job of the SDK and the instrumentation library
for each language), but to guarantee that when two different systems both
emit "the HTTP response status code," they use the same attribute name
(`http.response.status_code`) and the same value type — so that a query, a
dashboard, or an alert written against that name works identically no
matter where the data comes from.

This looks like a minor administrative detail until you're faced with the
alternative: a system with dozens of services across two languages, where
every team independently chooses attribute names, inevitably ends up with
`status_code`, `statusCode`, `http_status`, and `response_code` as four
different names for the same thing across four different services — which
means any dashboard that wants to show errors *across all services* either
has to count four times, or someone has to normalize the data after the
fact, usually right when speed matters most — during an incident.

**Resource attributes** (which describe *where* telemetry comes from —
service, version, environment, instance — as opposed to attributes on an
individual span or measurement, which describe *what happened*) play a
particularly important role per the official documentation: they're
attached once, at SDK initialization, and automatically accompany every
signal that process emits from then on — which makes them the natural place
to solve exactly the problem from the previous paragraph, once, in one place
per service, instead of repeating it at every instrumentation point.

### Why this justifies a different approach per language, instead of making it a risk

It's worth explicitly noting what would have happened had the decision gone
the other way — had both languages been required to use an identical
instrumentation mechanism (say, both forced into explicit SDK setup, or both
forced into an auto-instrumentation agent regardless of how mature that
technique is in the given language).

Had Python services been forced into a fully automatic, "zero-code"
approach modeled on the Java agent, the team would have inherited the
fragility Python's monkey-patching approach has relative to Java's bytecode
approach — silently failed instrumentation when a library version gets
updated, with no clear signal that it happened, discovered only when someone
notices traces are missing for a service that was "supposed" to be
instrumented. Conversely, had Java services been forced into explicit SDK
setup modeled on Python, the team would have sacrificed exactly the
advantage that makes the Java agent worthwhile — instant instrumentation of
a new application with zero lines of code — for no real benefit in return,
since the Java agent doesn't have the structural fragility the Python
monkey-patching approach has.

The point for the reader: OpenTelemetry deliberately standardizes the
boundary (OTLP, semantic conventions, resource attributes), and deliberately
does *not* standardize the mechanism per language — because that other
choice would force at least one language into an implementation technique
that doesn't suit it. When a standard leaves something open, it's worth
checking whether that's space deliberately left for a local decision, before
reading it as a gap in the standard.

## 2.4 Rules collected from this chapter

- Choose the instrumentation mechanism (auto-instrumentation agent vs.
  explicit SDK setup) based on how mature that technique is in the specific
  language, not for consistency with other languages in the portfolio.
- Never invent your own attribute name for a concept that already has a
  name in the semantic conventions — check first, even when your case
  "looks" uncovered.
- Set resource attributes once, at initialization, and treat them as a
  contract every service in the system must honor identically — that's the
  cheapest place to prevent four different names for the same thing.
- OTLP is why switching observability platforms should be the gateway
  layer's job, not every individual application's — check whether your
  system is actually organized that way, or whether that's just a
  declared assumption.
- When a standard leaves something open (like the instrumentation mechanism
  per language), assume it's deliberate, and look for the reason before
  trying to "align" it for the sake of consistency.

## 2.5 Exercise for the reader

Take two services in your system written in different languages and compare
what name each uses for the same concept — HTTP status code, the name of
the database it talks to, or call duration. If the names differ, look up the
right name in the official semantic conventions and check whether at least
one of the two services is already deviating from them for no reason —
that's a concrete, small fix that immediately pays off the next dashboard
you try to build across both services.

---

### Sources used in the analytical section

- [OpenTelemetry Protocol (OTLP) Specification](https://opentelemetry.io/docs/specs/otlp/)
- [Semantic Conventions — OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/)
- [Resource Semantic Conventions — OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/resource/)
- [OpenTelemetry Java Agent — Zero-code instrumentation](https://opentelemetry.io/docs/zero-code/java/agent/)
- [OpenTelemetry Python — Zero-code instrumentation](https://opentelemetry.io/docs/zero-code/python/)
- [History of OpenTelemetry — CNCF](https://opentelemetry.io/docs/what-is-opentelemetry/)
