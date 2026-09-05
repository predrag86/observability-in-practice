# KubeCon + CloudNativeCon EU 2027 — CFP draft
## Source: Chapter 28, "AI-assisted observability: an agent that reads telemetry"

Submission portal: https://sessionize.com/cncf-hosted-co-located-events-europe-2027/
Deadline: **Oct 18, 2026, 23:59 CET**. Notifications: Dec 14, 2026. Event: Mar 15, 2027, Barcelona.

Target track(s): **Observability Day** (primary) and/or **Agentics Day: MCP + Agents**
(content fits both — pick one as primary if the form forces a single choice, or submit to
both if it allows multiple; verify on the actual Sessionize form, which needs a login to see).

Format recommendation: **Solo presentation, 25 min.** The four-incident replay + the two
failure mechanisms (false success, wrong-store zero) need the room a 10-min lightning talk
doesn't give.

---

## Title (pick one, or mix)

1. **"The Agent Said 'Successfully Deleted.' Nothing Was Deleted."**
   *Lessons from testing an AI agent against four real observability incidents*
2. **"Replaying Incidents on an AI Agent: Where It's Right, and Where It Confidently Lies"**
3. **"The Missing Context Layer: What an AI Agent Doesn't Know About Your Telemetry"**
4. **"Four Real Incidents, One AI Agent: A Production Test of MCP-Based Observability"**

Recommendation: **#1** as the title (it's the concrete, quotable hook that makes a reviewer
stop scrolling), with **#3's phrase** ("the missing context layer") as a good subtitle if the
form has a separate subtitle field.

---

## Abstract / session description (~210 words — trim to fit the actual field limit)

Every major telemetry vendor now ships an MCP server, and the pitch is the same everywhere:
give an AI agent read access to your metrics, logs and traces, and it will speed up alert
triage. We didn't take that promise on faith. Instead, we replayed four real, already-resolved
incidents from our own production history through an agent with the same MCP-based query tools
a human on-call engineer has, and compared its reasoning to the answer we already knew.

Two replays went well — the agent independently reconstructed the correct root cause through a
chain of evidence a human would recognize. One replay is the one worth your 25 minutes: without
extra context, the agent read a derived health metric, took it at face value, and would have
confidently escalated a false outage — because nothing in generic observability knowledge told
it that metric was known to lie. And in testing the agent's write boundary, we found a sharper
problem: a blocked write and a successful one return an *identical* "success" message, so the
agent will honestly report an action that never happened.

This talk covers what we built in response — a small, on-demand "context layer" of
system-specific pitfalls, and enforcing read-only access at the token's permission scope rather
than trusting the agent's self-report — and what four real incidents taught us about where
agent-assisted observability is ready today, and where it isn't yet.

---

## Notes for reviewers / "is this a case study" field

Yes — this is a production case study, not a demo or a vendor pitch. All four incidents
replayed are real, already-resolved production incidents (details anonymized: company name,
internal domains and resource IDs are generalized, consistent with how the source material —
a full-length book on this production observability implementation — already handles this).
The talk includes: the replay methodology, the four incidents and what each one exposed, two
concrete named failure mechanisms (false success on a blocked action; querying the structurally
wrong data store, which returns a convincing zero instead of an error), the context-layer
mitigation, and where this is independently confirmed by existing MCP/AI-SRE guidance (cited
in the talk) versus where our finding is new. Closes with a clear, actionable recommendation on
where to draw the human-approval line today.

## Relevant CNCF / ecosystem projects to list

- OpenTelemetry (the telemetry the agent queries)
- Prometheus / the query surface the MCP tool exposes (metrics)
- Model Context Protocol (the connector standard this whole talk is about)
- Grafana (Loki/Tempo/Mimir) as the platform, if the form allows non-CNCF context

## One-line pitch (for a social/preview card, if the form asks)

We gave an AI agent MCP access to our telemetry and tested it against four real incidents —
here's exactly where it got the diagnosis right, where it confidently got it wrong, and the one
architectural decision that kept "confidently wrong" from becoming "silently destructive."

---

## Speaker bio (draft — please adjust to taste)

Predrag Mujkovic is a Senior DevOps/SRE engineer with close to a decade of experience across
cloud and on-premises infrastructure, currently running observability for a weather-data
analytics platform on AWS (ECS Fargate, Aurora/RDS, Terraform) with OpenTelemetry and the
Grafana LGTM stack (Loki, Grafana, Tempo, Mimir). He is the author of a full-length book
documenting that platform's observability implementation from the ground up, based on the real
production system.

---

## Before you submit — things to double check

1. Confirm the actual title/abstract character limits on the live Sessionize form (they're
   not published on the public CFP page) and trim the abstract above to fit.
2. Confirm whether the form lets you pick more than one target co-located event, or forces a
   single choice — decide Observability Day vs. Agentics Day accordingly.
3. The CFP explicitly asks you to flag if a submission is similar to a previously-presented
   talk and explain how it differs — not an issue here since this hasn't been presented before,
   but worth a one-line note if the form asks.
4. Panel format needs 3 speakers from 3 different organizations — not relevant here since this
   is a solo submission, just flagging in case you want to explore a panel version later.
