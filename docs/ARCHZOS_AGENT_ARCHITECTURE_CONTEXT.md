# ArchzOS Agent Architecture Context

`agent-shift-handoff` is the session-continuity layer for long-running agent
workflows.

## 1) Why this repo exists

Long-running agent tasks fail when context is truncated or summaries drop
critical state. This repo externalizes the state needed to resume cleanly.

## 2) Where it fits

- `trifecta-guard`: runtime security enforcement.
- `rewardhack-probe`: reward-hacking demos and probe batteries.
- `mcp-sentinel`: MCP supply-chain watchdog.
- `agent-shift-handoff`: structured handoff and resume verification.

## 3) Boundary

This repo is standalone OSS tooling. It is not a current production dependency
of archzOS apps; the fit is deliberate and forward-looking.

## 4) Storage choice

SQLite is the correct storage choice here because the workload is keyed,
session-local, and portable across restarts without a running service.

## 5) NEXUS-50 fit

The forward-looking deployment fit is a 50-agent orchestration context with
multi-day task horizons (NEXUS-50). In that setting, session boundaries are a
certainty, not an edge case, and deterministic handoff + verification is
required to prevent regressions when context windows roll.
