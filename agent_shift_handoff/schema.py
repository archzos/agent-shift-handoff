"""Versioned JSON Schema for HandoffDocument."""

from __future__ import annotations

HANDOFF_SCHEMA_VERSION = "1.0"

HANDOFF_SCHEMA: dict[str, object] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "session_id",
        "agent_id",
        "produced_at",
        "task",
        "artifacts",
        "environment",
        "decision_log",
        "open_questions",
        "resume_instructions",
        "continuity_score",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": HANDOFF_SCHEMA_VERSION},
        "session_id": {"type": "string"},
        "agent_id": {"type": "string"},
        "produced_at": {"type": "string"},
        "task": {
            "type": "object",
            "additionalProperties": False,
            "required": ["goal", "status", "completed_steps", "pending_steps", "blocked_steps"],
            "properties": {
                "goal": {"type": "string"},
                "status": {"type": "string", "enum": ["IN_PROGRESS", "BLOCKED", "COMPLETED"]},
                "completed_steps": {"type": "array", "items": {"type": "string"}},
                "pending_steps": {"type": "array", "items": {"type": "string"}},
                "blocked_steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["step", "reason"],
                        "properties": {
                            "step": {"type": "string"},
                            "reason": {"type": "string"},
                        },
                    },
                },
            },
        },
        "artifacts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["path", "state", "checksum", "notes"],
                "properties": {
                    "path": {"type": "string"},
                    "state": {"type": "string", "enum": ["CREATED", "MODIFIED", "BROKEN", "DELETED"]},
                    "checksum": {"type": "string"},
                    "notes": {"type": "string"},
                },
            },
        },
        "environment": {
            "type": "object",
            "additionalProperties": False,
            "required": ["tool_versions", "active_processes", "external_dependencies"],
            "properties": {
                "tool_versions": {"type": "object", "additionalProperties": {"type": "string"}},
                "active_processes": {"type": "array", "items": {"type": "string"}},
                "external_dependencies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name", "state"],
                        "properties": {
                            "name": {"type": "string"},
                            "state": {"type": "string"},
                        },
                    },
                },
            },
        },
        "decision_log": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["decision", "rationale", "timestamp"],
                "properties": {
                    "decision": {"type": "string"},
                    "rationale": {"type": "string"},
                    "timestamp": {"type": "string"},
                },
            },
        },
        "open_questions": {"type": "array", "items": {"type": "string"}},
        "resume_instructions": {
            "type": "object",
            "additionalProperties": False,
            "required": ["first_actions", "verification_checks", "known_risks"],
            "properties": {
                "first_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                "verification_checks": {"type": "array", "items": {"type": "string"}},
                "known_risks": {"type": "array", "items": {"type": "string"}},
            },
        },
        "continuity_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
}
