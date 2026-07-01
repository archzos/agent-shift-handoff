# Handoff Schema Spec

`agent-shift-handoff` uses schema version `1.0`.

## Fields

- `schema_version`: literal string `1.0`
- `session_id`: UUID string
- `agent_id`: string identifier for the agent
- `produced_at`: ISO8601 timestamp
- `task`: current task state
- `artifacts`: tracked files and checksums
- `environment`: tools, processes, dependencies
- `decision_log`: important decisions and rationale
- `open_questions`: unresolved questions
- `resume_instructions`: first actions and verification checks
- `continuity_score`: float from `0.0` to `1.0`

## Validation rules

- `continuity_score < 0.7` is considered degraded.
- `first_actions[0]` must be a verification step.
- Artifact checksums are required when files are tracked.
