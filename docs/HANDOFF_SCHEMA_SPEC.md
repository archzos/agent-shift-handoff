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

## Versioning policy

- Minor-compatible additions:
  - additive optional fields are allowed inside existing objects.
  - existing field meaning and type cannot change.
- Breaking changes:
  - required-field addition, field removal, or type change requires a major schema version.
  - loaders/verifiers must reject unsupported major versions with explicit guidance.
- Compatibility contract:
  - a `1.x` producer must remain readable by all `1.x` verifiers.
  - migration notes are mandatory for any breaking revision.

## Migration notes requirements

When schema changes:
- document old -> new field mapping and default behavior.
- provide one upgrade example payload and one downgrade risk note.
- update `docs/FAILURE_MODES.md` with at least one new degraded/resume failure mode if applicable.

## Valid examples

### Valid example A (minimal)

```json
{
  "schema_version": "1.0",
  "session_id": "3dd85868-74cf-4609-ab30-64ee46381ea8",
  "agent_id": "coder-01",
  "produced_at": "2026-07-01T12:30:00Z",
  "task": {
    "goal": "Ship issue fix",
    "status": "in_progress",
    "first_actions": ["verify current branch and tests"]
  },
  "artifacts": [
    {
      "path": "src/app.py",
      "checksum": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
    }
  ],
  "environment": {"tools": ["git", "pytest"]},
  "decision_log": [{"decision": "Prioritize bugfix", "why": "blocks release"}],
  "open_questions": [],
  "resume_instructions": {"first_actions": ["verify current branch and tests"]},
  "continuity_score": 0.82
}
```

### Valid example B (degraded continuity)

```json
{
  "schema_version": "1.0",
  "session_id": "d30e8574-67cf-4bf8-b40d-8df7e27eeebb",
  "agent_id": "triage-02",
  "produced_at": "2026-07-01T12:31:00Z",
  "task": {
    "goal": "Resume failed run",
    "status": "blocked",
    "first_actions": ["verify artifact drift before execution"]
  },
  "artifacts": [],
  "environment": {"tools": ["python"]},
  "decision_log": [],
  "open_questions": ["Need updated API key"],
  "resume_instructions": {"first_actions": ["verify artifact drift before execution"]},
  "continuity_score": 0.65
}
```

## Invalid examples

### Invalid example 1: wrong schema version type

```json
{
  "schema_version": 1.0,
  "session_id": "3dd85868-74cf-4609-ab30-64ee46381ea8"
}
```

Reason: `schema_version` must be a literal string.

### Invalid example 2: missing checksum for tracked artifact

```json
{
  "schema_version": "1.0",
  "session_id": "3dd85868-74cf-4609-ab30-64ee46381ea8",
  "agent_id": "coder-01",
  "produced_at": "2026-07-01T12:30:00Z",
  "task": {"first_actions": ["verify branch"]},
  "artifacts": [{"path": "src/app.py"}],
  "environment": {},
  "decision_log": [],
  "open_questions": [],
  "resume_instructions": {"first_actions": ["verify branch"]},
  "continuity_score": 0.82
}
```

Reason: artifact entries require checksums when files are tracked.

### Invalid example 3: first action is not a verification step

```json
{
  "schema_version": "1.0",
  "session_id": "3dd85868-74cf-4609-ab30-64ee46381ea8",
  "agent_id": "coder-01",
  "produced_at": "2026-07-01T12:30:00Z",
  "task": {"first_actions": ["start coding immediately"]},
  "artifacts": [],
  "environment": {},
  "decision_log": [],
  "open_questions": [],
  "resume_instructions": {"first_actions": ["start coding immediately"]},
  "continuity_score": 0.82
}
```

Reason: `first_actions[0]` must be a verification step.
