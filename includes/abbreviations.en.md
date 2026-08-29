*[absence-class alert]: A problem that doesn't manifest as a wrong signal, but as the absence of a signal that should exist.
*[active series]: Time series that are currently receiving data points.
*[billable series]: What the provider actually charges for — rarely the same number as active series.
*[Adaptive Traces]: Trace sampling where the observability platform, not the collector, decides what to keep, based on ordered policies.
*[blast radius]: How many users, services, or records would be affected if something goes wrong.
*[burn-rate]: How fast an SLO's error budget is being consumed, expressed as a multiple of the normal rate.
*[Dead man's switch]: An alert designed to fire when the mechanism that would normally report a problem stops working.
*[dedup]: Grouping repeated notifications about the same failure into a single record within a time window.
*[DPM]: Data points per minute — how many data points per minute a single series produces.
*[error budget]: The allowed amount of "bad" behavior before an SLO is breached.
*[Exemplar]: A single sample (usually one span/trace ID) linked to a point on a metric histogram.
*[golden signals]: Latency, traffic, errors, saturation — the core four dimensions for judging a service's health.
*[Keyed-HMAC pseudonymization]: Turning an identifier into a pseudonym using a hash function with a secret key, resisting brute-force attacks.
*[MCP]: Model Context Protocol — an open protocol giving an AI agent structured access to tools and data.
*[native histogram]: A histogram format where the bucket distribution is sent more compactly than a classic fixed-bucket histogram.
*[POA&M]: Plan of Action and Milestones — an item not yet resolved but actively tracked toward resolution.
*[RED method]: Rate, Errors, Duration — the standard framework for services that continuously receive traffic.
*[resource attribute]: A key-value pair describing the source of telemetry, e.g. service.name.
*[risk acceptance]: A documented decision to knowingly not resolve a risk, with a rationale and a date.
*[semantic conventions]: Standardized attribute and metric names that OTel prescribes, e.g. http.status_code.
*[SLI]: Service Level Indicator — a measurable signal, e.g. the percentage of successful requests.
*[SLO]: Service Level Objective — a target value for a signal over time, e.g. 99.9%.
*[span metrics]: Metrics derived from spans (traces) before any sampling.
*[tail sampling]: The decision to keep a span is made after the whole span completes.
*[target_info]: A standard OTel/Prometheus metric that carries resource attributes as labels.
*[tier]: A classification of alerts by severity that determines dedup and notification routing.
*[USE method]: Utilization, Saturation, Errors — a framework for observing resources (host, disk, network).
*[watcher-outlives-the-watched]: An alert monitoring the observability platform itself must have a path to a human independent of that platform.
