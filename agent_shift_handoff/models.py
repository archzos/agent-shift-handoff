"""Core models for structured handoff documents and verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BlockedStep:
    step: str
    reason: str


@dataclass(slots=True)
class TaskState:
    goal: str
    status: str
    completed_steps: list[str]
    pending_steps: list[str]
    blocked_steps: list[BlockedStep] = field(default_factory=list)


@dataclass(slots=True)
class ArtifactState:
    path: str
    state: str
    checksum: str
    notes: str


@dataclass(slots=True)
class ExternalDependencyState:
    name: str
    state: str


@dataclass(slots=True)
class EnvironmentState:
    tool_versions: dict[str, str]
    active_processes: list[str]
    external_dependencies: list[ExternalDependencyState] = field(default_factory=list)


@dataclass(slots=True)
class DecisionEntry:
    decision: str
    rationale: str
    timestamp: str


@dataclass(slots=True)
class ResumeInstructions:
    first_actions: list[str]
    verification_checks: list[str]
    known_risks: list[str]


@dataclass(slots=True)
class HandoffDocument:
    schema_version: str
    session_id: str
    agent_id: str
    produced_at: str
    task: TaskState
    artifacts: list[ArtifactState]
    environment: EnvironmentState
    decision_log: list[DecisionEntry]
    open_questions: list[str]
    resume_instructions: ResumeInstructions
    continuity_score: float
    raw_state: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VerificationResult:
    status: str
    issues: list[str]
    artifact_drifts: list[str]


def handoff_to_dict(document: HandoffDocument, include_internal: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": document.schema_version,
        "session_id": document.session_id,
        "agent_id": document.agent_id,
        "produced_at": document.produced_at,
        "task": {
            "goal": document.task.goal,
            "status": document.task.status,
            "completed_steps": document.task.completed_steps,
            "pending_steps": document.task.pending_steps,
            "blocked_steps": [{"step": item.step, "reason": item.reason} for item in document.task.blocked_steps],
        },
        "artifacts": [
            {"path": item.path, "state": item.state, "checksum": item.checksum, "notes": item.notes}
            for item in document.artifacts
        ],
        "environment": {
            "tool_versions": document.environment.tool_versions,
            "active_processes": document.environment.active_processes,
            "external_dependencies": [
                {"name": item.name, "state": item.state} for item in document.environment.external_dependencies
            ],
        },
        "decision_log": [
            {"decision": item.decision, "rationale": item.rationale, "timestamp": item.timestamp}
            for item in document.decision_log
        ],
        "open_questions": document.open_questions,
        "resume_instructions": {
            "first_actions": document.resume_instructions.first_actions,
            "verification_checks": document.resume_instructions.verification_checks,
            "known_risks": document.resume_instructions.known_risks,
        },
        "continuity_score": document.continuity_score,
    }
    if include_internal:
        payload["raw_state"] = document.raw_state
    return payload


def handoff_from_dict(payload: dict[str, Any]) -> HandoffDocument:
    return HandoffDocument(
        schema_version=str(payload["schema_version"]),
        session_id=str(payload["session_id"]),
        agent_id=str(payload["agent_id"]),
        produced_at=str(payload["produced_at"]),
        task=TaskState(
            goal=str(payload["task"]["goal"]),
            status=str(payload["task"]["status"]),
            completed_steps=list(payload["task"]["completed_steps"]),
            pending_steps=list(payload["task"]["pending_steps"]),
            blocked_steps=[BlockedStep(step=item["step"], reason=item["reason"]) for item in payload["task"]["blocked_steps"]],
        ),
        artifacts=[
            ArtifactState(path=item["path"], state=item["state"], checksum=item["checksum"], notes=item["notes"])
            for item in payload["artifacts"]
        ],
        environment=EnvironmentState(
            tool_versions=dict(payload["environment"]["tool_versions"]),
            active_processes=list(payload["environment"]["active_processes"]),
            external_dependencies=[
                ExternalDependencyState(name=item["name"], state=item["state"])
                for item in payload["environment"]["external_dependencies"]
            ],
        ),
        decision_log=[
            DecisionEntry(decision=item["decision"], rationale=item["rationale"], timestamp=item["timestamp"])
            for item in payload["decision_log"]
        ],
        open_questions=list(payload["open_questions"]),
        resume_instructions=ResumeInstructions(
            first_actions=list(payload["resume_instructions"]["first_actions"]),
            verification_checks=list(payload["resume_instructions"]["verification_checks"]),
            known_risks=list(payload["resume_instructions"]["known_risks"]),
        ),
        continuity_score=float(payload["continuity_score"]),
        raw_state=dict(payload.get("raw_state", {})),
    )
