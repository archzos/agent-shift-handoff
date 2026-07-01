"""Deterministic session compaction helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from agent_shift_handoff.state_store.sqlite_store import add_note


def compact_steps(completed_steps: list[str]) -> list[str]:
    compacted = []
    for step in completed_steps:
        title = step.split(":", 1)[0].strip()
        outcome = "done" if "done" in step.lower() or "complete" in step.lower() else "recorded"
        compacted.append(f"{title} [{outcome}]")
    return compacted


def checkpoint_notes(db_path: str, session_id: str, completed_steps: list[str]) -> list[str]:
    compacted = compact_steps(completed_steps)
    add_note(db_path, session_id, " | ".join(compacted), datetime.now(timezone.utc).isoformat())
    return compacted
