"""Handoff document generator."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from jsonschema import ValidationError, validate

from agent_shift_handoff.models import (
    HandoffDocument,
    handoff_from_dict,
)
from agent_shift_handoff.schema import HANDOFF_SCHEMA


HANDOFF_PROMPT_TEMPLATE = """You are generating a structured session handoff for a long-running coding agent.
Return ONLY JSON matching the schema below.

Schema:
{schema_json}

Requirements:
- Be specific and actionable.
- completed_steps should be compact but exact.
- pending_steps must start with a verb and be executable without rereading the full history.
- first_actions[0] must be a verification step.
- Score continuity conservatively.
- Prefer 5 precise claims over 20 vague claims.
- Do not use placeholders like "continue working", "resume", or "do next steps".

High-quality example:
{high_quality_example}
Why high-quality:
- Uses concrete files and checksums
- first_actions[0] is explicit verification
- pending_steps are executable verbs

Low-quality example:
{low_quality_example}
Why low-quality:
- Vague pending step ("continue")
- Non-specific resume instruction
- Missing practical verification detail
"""


class MockHandoffClient:
    """Deterministic handoff generator used in tests and dry-runs."""

    def generate(self, prompt: str, state: dict[str, Any]) -> dict[str, Any]:
        touched = state.get("touched_files", [])
        artifacts = []
        for path in touched:
            artifacts.append(
                {
                    "path": path,
                    "state": "MODIFIED",
                    "checksum": state.get("checksums", {}).get(path, ""),
                    "notes": "tracked by mock generator",
                }
            )
        return {
            "schema_version": "1.0",
            "session_id": state.get("session_id", "unknown-session"),
            "agent_id": state.get("agent_id", "mock-agent"),
            "produced_at": datetime.now(timezone.utc).isoformat(),
            "task": {
                "goal": state.get("goal", ""),
                "status": state.get("status", "IN_PROGRESS"),
                "completed_steps": state.get("completed_steps", []),
                "pending_steps": state.get("pending_steps", []),
                "blocked_steps": state.get("blocked_steps", []),
            },
            "artifacts": artifacts,
            "environment": state.get(
                "environment",
                {
                    "tool_versions": {},
                    "active_processes": [],
                    "external_dependencies": [],
                },
            ),
            "decision_log": state.get("decision_log", []),
            "open_questions": state.get("open_questions", []),
            "resume_instructions": state.get(
                "resume_instructions",
                {
                    "first_actions": ["verify the latest artifact checksums"],
                    "verification_checks": ["compare checksums for touched files"],
                    "known_risks": [],
                },
            ),
            "continuity_score": state.get("continuity_score", 0.8),
        }


class BedrockHandoffClient:
    """Future-compatible Bedrock path."""

    def __init__(self, model: str | None = None, region: str | None = None) -> None:
        self.model = model
        self.region = region

    def generate(self, prompt: str, state: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Bedrock handoff generation is reserved for live deployment")


def _validate_document(document: dict[str, Any]) -> None:
    validate(instance=document, schema=HANDOFF_SCHEMA)


def build_prompt(state: dict[str, Any]) -> str:
    high_quality_example = json.dumps(
        {
            "schema_version": "1.0",
            "session_id": "11111111-1111-1111-1111-111111111111",
            "agent_id": "langgraph-agent",
            "produced_at": "2026-07-01T12:00:00Z",
            "task": {
                "goal": "Implement a checksum verifier",
                "status": "IN_PROGRESS",
                "completed_steps": ["Added checksum helper"],
                "pending_steps": ["Implement verification for tracked files"],
                "blocked_steps": [],
            },
            "artifacts": [
                {"path": "agent_shift_handoff/verifier.py", "state": "MODIFIED", "checksum": "abc123", "notes": "verification logic stubbed"}
            ],
            "environment": {"tool_versions": {"python": "3.11"}, "active_processes": [], "external_dependencies": []},
            "decision_log": [{"decision": "Use SQLite", "rationale": "portable session store", "timestamp": "2026-07-01T12:01:00Z"}],
            "open_questions": ["Should verification require checksum drift warnings?"],
            "resume_instructions": {
                "first_actions": ["verify agent_shift_handoff/verifier.py checksum", "load the current handoff", "continue implementing verifier tests"],
                "verification_checks": ["file exists", "checksum matches"],
                "known_risks": ["artifact drift between sessions"],
            },
            "continuity_score": 0.92,
        },
        indent=2,
    )
    low_quality_example = json.dumps(
        {
            "schema_version": "1.0",
            "session_id": "bad",
            "agent_id": "agent",
            "produced_at": "now",
            "task": {"goal": "do work", "status": "IN_PROGRESS", "completed_steps": [], "pending_steps": ["continue"], "blocked_steps": []},
            "artifacts": [],
            "environment": {"tool_versions": {}, "active_processes": [], "external_dependencies": []},
            "decision_log": [],
            "open_questions": [],
            "resume_instructions": {"first_actions": ["continue working"], "verification_checks": [], "known_risks": []},
            "continuity_score": 0.4,
        },
        indent=2,
    )
    return HANDOFF_PROMPT_TEMPLATE.format(
        schema_json=json.dumps(HANDOFF_SCHEMA, indent=2),
        high_quality_example=high_quality_example,
        low_quality_example=low_quality_example,
    ) + "\nSTATE:\n" + json.dumps(state, indent=2)


def generate_handoff(state: dict[str, Any], client: Any | None = None, retries: int = 1) -> HandoffDocument:
    prompt = build_prompt(state)
    client = client or MockHandoffClient()
    last_error: str | None = None
    for attempt in range(retries + 1):
        payload = client.generate(prompt, state)
        try:
            _validate_document(payload)
            return handoff_from_dict(payload)
        except ValidationError as exc:
            last_error = str(exc)
            state = {**state, "generation_error": last_error}
            prompt = f"{prompt}\n\nValidation error from previous attempt:\n{last_error}\nRegenerate fully valid JSON."
    degraded = MockHandoffClient().generate(prompt, state)
    degraded["continuity_score"] = min(float(degraded.get("continuity_score", 0.5)), 0.5)
    _validate_document(degraded)
    document = handoff_from_dict(degraded)
    document.raw_state = {**state, "generation_error": last_error, "degraded": True}
    return document
