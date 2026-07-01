"""Handoff loading into a resumed session."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_shift_handoff.models import HandoffDocument
from agent_shift_handoff.verifier import verify_handoff


def load_handoff(document: HandoffDocument, agent: Any, base_dir: str | Path = ".") -> dict[str, Any]:
    verification = verify_handoff(document, base_dir=base_dir)
    if verification.status == "INVALID":
        raise ValueError(f"invalid handoff: {verification.issues}")
    agent.load_state(_document_to_context(document, verification))
    return {
        "verification": verification,
        "context": _document_to_context(document, verification),
    }


def _document_to_context(document: HandoffDocument, verification) -> dict[str, Any]:
    return {
        "handoff": document,
        "task_goal": document.task.goal,
        "pending_steps": document.task.pending_steps,
        "completed_steps": document.task.completed_steps,
        "artifact_drifts": verification.artifact_drifts,
        "resume_instructions": document.resume_instructions.first_actions,
        "continuity_score": document.continuity_score,
    }
