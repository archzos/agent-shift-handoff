"""LangGraph adapter for structured handoff generation and loading."""

from __future__ import annotations


class LangGraphAgentAdapter:
    """Minimal adapter stub for LangGraph-style state graphs."""

    def __init__(self, state: dict | None = None, touched_files: list[str] | None = None) -> None:
        self._state = state or {}
        self._touched_files = touched_files or []

    def get_state(self) -> dict:
        return self._state

    def load_state(self, handoff: dict) -> None:
        self._state = {"loaded_handoff": handoff}

    def touched_files(self) -> list[str]:
        return list(self._touched_files)
