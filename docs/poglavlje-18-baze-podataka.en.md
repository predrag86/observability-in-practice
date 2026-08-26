# Chapter 18 — Databases (managed, RDS/Aurora-type)

The dashboard in a car and the diagnostic port at the mechanic's show two
different cars, even though they're looking at the same engine. The panel in
front of the driver reports speed, RPM, coolant temperature, fuel level —
everything needed to drive safely, measured from outside, from sensors the
manufacturer judged sufficient for a driver. A mechanic who plugs in a
diagnostic reader sees something entirely different: fault codes per
individual cylinder, the history of oxygen sensor readings, how many times
the transmission dropped into limp mode last month. Neither view is lying.
But a driver who watches only the dashboard will never learn that one
cylinder has been misfiring irregularly for two weeks now — because that
information was simply never designed to reach the dashboard. And a
mechanic who watches only the diagnostics will never know whether the car
is even moving at that moment. A managed database is observed in exactly
the same way: from outside, through the dashboard the provider supplies,
and from inside, through the diagnostics the database engine itself
supplies.

## 18.1 The question this chapter answers

The database is managed by the provider — you can't SSH into the instance,
the disk isn't directly visible, the process can't be profiled with a tool
running on the host. So what can actually be observed, with how much
confidence, and why does any single view — whether external or internal —
systematically miss half of the problems that actually occur?

## 18.2 How it's done — a practical overview

### Two layers, neither a subset of the other

The implementation this book follows observes the managed relational
database through two independent collection layers, deliberately without
trying to reduce one to the other:

- **The external layer** — metrics the provider exposes at the instance and
  virtualization level: CPU, memory, IOPS, read/write latency, connection
  count, free disk space, replica lag. This is the "how busy is the
  machine" view — enough to notice that something's wrong, never enough to
  say **what**.
- **The internal layer** — an exporter that connects directly to the
  database engine itself and reads its internal system tables: active
  sessions, locks, per-table and per-index statistics, replication slots,
  long-running queries. This is the "what the database is actually doing"
  view — it sees things the external layer structurally cannot, because
  they never exist outside the database process itself.

The key decision, stated explicitly in the implementation's documentation:
**neither layer is a superset of the other.** A connection leak is visible
in the internal layer (the count of open sessions by user, by state) long
before the external layer notices any rise in latency at all. Conversely, a
total loss of network reachability to the instance itself is visible
**only** from outside — because at that moment the internal exporter can't
even connect to report anything.

### A separate, easily forgotten alert: the monitoring itself went down, not the database

The implementation explicitly separates two different claims that are easy
to conflate: "the database isn't working" and "the exporter watching the
database isn't working." If the process that scrapes the internal layer
crashes, stops, or loses its credential, every dashboard built on the
internal layer suddenly goes empty. Without a dedicated alert, that empty
dashboard looks identical to "everything is quiet" — which is more
dangerous than any real alert, because no one is paged until someone
happens to notice that the graph hasn't moved a single point in a week. The
implementation keeps a separate, independent alert that watches only
whether the internal layer is delivering fresh data at all, entirely
separate from any threshold based on the content of that data.

### TLS only to the instance, never through an intermediary

The connection the internal exporter uses to read the system tables goes
exclusively to the **single-instance endpoint**, with full TLS certificate
and hostname verification — never to the cluster/reader endpoint used for
load balancing, and never through a connection-pooling proxy. The reason is
structural, not a matter of taste: the load-balancing endpoint can redirect
the connection to a different physical instance at any moment, and a
pooling proxy by definition shares a single backend connection among
multiple clients in turn. In both cases, the mapping "this session in the
internal table belongs to this specific instance/client" stops holding —
and that mapping is exactly what the internal collection layer exists to
guarantee. Collection has to go directly to the instance to keep its
meaning.

### A lever at the database level, not the infrastructure level

When the internal layer detects sessions that stay open in the "idle in
transaction" state longer than is reasonable — the most common cause of a
slow connection leak — there's a lever available that doesn't require
changing application code: a timeout set at the database level itself that
forcibly terminates such a session after a defined period of inactivity.
This is deliberately configured as a last line of defense, not a first one
— the first line is still fixing the application that leaves transactions
open — but the lever exists precisely because application code doesn't
always get every caller fixed in time.

![Two independent collection layers over one managed database: external (the provider's instance metrics) and internal (an exporter directly on the engine), with a dedicated alert watching whether the internal layer is breathing at all.](diagrams/ch18-dve-ravni.png){: width="90%" }

![A connection leak visible from the inside from hour zero — the external layer (latency) doesn't notice the problem until 40 hours later, by which point the trend is already far along.](diagrams/dashboard-connections.png){: width="95%" }

## 18.3 Analytical section — two layers as a known but rarely named pattern

### The official recommendation agrees with the split, but doesn't name it explicitly

The provider's own documentation does distinguish three layers:
virtualization-level metrics (available immediately, free), an OS-level
agent on the instance (deeper insight into processes, with sampling
delay), and a layer that samples active database load and attributes it to
specific queries. All three layers still observe the database **from
outside** — none of them reads the database engine's own internal system
tables directly the way a dedicated exporter does. The split the
implementation uses — "outside" versus "inside" — corresponds most closely
to an older, more general split from the systems-reliability literature:
**black box** (observing behavior from outside, without access to internal
state) versus **white box** (instrumentation that reads a system's
internal state directly). The provider's load-sampling layer is closer to
white box than plain instance metrics, but it still doesn't replace direct
insight into the system tables — locks, per-index bloat, the exact text of
a long-running query in real time remain visible only to the dedicated
exporter.

### Where the standard changes the conclusion: the pooling proxy and session mapping

The official documentation for the connection-pooling proxy confirms
exactly what the implementation assumed without having read that
documentation: under normal operation, the proxy **borrows** a backend
connection per transaction and returns it to the shared pool immediately
afterward — which means the session identifier in the internal system
tables is shared and reused across many different clients over time.
There's also a built-in safety valve: when a session-state change occurs
that can't be safely shared (temporary tables, prepared statements, for
instance), the proxy **pins** to a fixed 1:1 connection for the rest of
that session — restoring trackability for that one connection, but at the
cost of losing pooling efficiency. The official warning is explicit:
widespread pinning "reduces the efficiency of connection reuse," and the
recommendation is to avoid its triggers in application code, not to rely
on pinning as a normal state. The practical consequence, confirmed by both
the implementation and the official documentation: session-level tracking
through the internal system tables is reliable only for connections that
go directly to the instance — exactly the reason the decision to bypass
the proxy and the load-balancing endpoint is a structural necessity, not
excessive caution.

### The "monitoring itself is down" alert as a known, but not AWS-native, pattern

The alert that checks whether the internal layer is delivering fresh data
at all, independent of that data's content, matches a well-known pattern
in the Prometheus/SRE world of alerting — often called a "dead man's
switch": an alert that, unlike every other alert, fires exactly when it
**stops** receiving heartbeats, catching a silent failure of the
monitoring pipeline itself (an exporter dying, a scrape target being lost)
that would otherwise go unnoticed as false quiet. It's worth noting that
this pattern isn't natively built into the provider's instance-metrics
platform — it's specific to Prometheus-style collection, where the absence
of data is distinguished from a data point of "zero." That means the
implementation has to build this alert itself, outside of what the
provider offers by default — which is exactly what was done.

### TLS verify-full as an officially recommended, not an arbitrary, setting

The official recommendation for production workloads handling sensitive
data explicitly ranks the levels of TLS connection verification: the
lowest levels provide no real protection, the middle level checks the
certificate chain but not the hostname, and the highest level — which
checks both the certificate signature and that the hostname matches the
server actually being connected to — is described as recommended for
every production workload that handles sensitive data. The implementation
uses exactly that highest level, and exclusively against the
single-instance endpoint — doubly aligned with the recommendation, once
through the verification level, once through the choice of endpoint.

### Counterfactual scenario: what the standard approach would miss

Picture a team that tracked only the provider's standard instance metrics,
without a dedicated exporter and without a dedicated alert for its
availability — a textbook, "good enough" approach. A connection leak would
first be noticed only once the connection count approached the limit and
latency started rising noticeably — meaning the problem would be caught at
the point when it was already close to a serious outage, instead of hours
or days earlier, while it was still just a trend in the count of "idle in
transaction" sessions. And even if the exporter had existed at all in such
a setup, without a dedicated alert for its availability, its failure would
look completely identical to "everything's fine" — an empty dashboard,
without a single alert, until someone happened to notice by hand that the
graph hadn't moved in days, and only when they needed it to diagnose a
completely different problem.

Let's return to the dashboard and the diagnostic port from the start of
the chapter. A driver who drives watching only the dashboard isn't driving
carelessly — they're driving with exactly as much information as the
dashboard was designed to give them, no more and no less. The problem
arises only when it's forgotten that the dashboard **isn't** the complete
picture of the engine, and when the diagnostic port gets plugged in only
after a failure, instead of regularly, as a second, equally legitimate
source of truth.

## 18.4 Rules collected from this chapter

- Track the managed database through two independent layers — external
  (the provider's instance metrics) and internal (an exporter directly on
  the engine) — and don't try to reduce one to the other; each sees things
  the other structurally cannot.
- Keep a separate, independent alert that checks only whether the internal
  layer is delivering fresh data at all — an empty dashboard with no
  alerts firing is more dangerous than a dashboard full of alerts, because
  it looks identical to "everything's quiet."
- Connect the internal exporter exclusively to the single-instance
  endpoint, with full TLS hostname verification — never through a
  load-balancing endpoint or a pooling proxy, since both erase the
  session-to-instance mapping the internal layer exists to guarantee.
- When you find sessions stuck "idle in transaction," use a timeout at the
  database level as a last line of defense — not as a substitute for
  fixing the application code that leaves them open.
- Don't measure the success of monitoring by whether the dashboard looks
  quiet — measure it by whether you know, with certainty, whether that
  quiet is real or just an absence of data.

## 18.5 Exercise for the reader

Check whether your team has a dedicated alert that tracks only the
availability of the database metrics-collection mechanism itself —
independent of any threshold based on the content of those metrics. If no
such alert exists, imagine a scenario where that mechanism stops working
on a Friday evening: how long would pass before someone noticed that the
dashboard they've been looking at hasn't shown anything new for days?

---

### Sources used in the analytical section

- [Monitoring tools for Amazon Aurora — AWS Aurora User Guide](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/MonitoringOverview.html)
- [Monitoring OS metrics with Enhanced Monitoring — AWS Aurora User Guide](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_Monitoring.OS.html)
- [Chapter 6: Monitoring Distributed Systems — Google SRE Book](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Avoiding pinning an RDS Proxy — AWS RDS User Guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-pinning.html)
- [RDS Proxy concepts and terminology — AWS RDS User Guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.howitworks.html)
- [Securing Your Monitoring Stack with a Dead Man's Switch](https://seifrajhi.github.io/blog/securing-monitoring-stack-dead-man-switch/)
- [Enforcing TLS and managing certificate rotation for RDS and Aurora PostgreSQL — AWS Database Blog](https://aws.amazon.com/blogs/database/enforcing-tls-and-managing-certificate-rotation-for-rds-and-amazon-aurora-postgresql/)
