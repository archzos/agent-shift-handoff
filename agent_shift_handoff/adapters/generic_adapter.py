"""Bring-your-own-agent adapter interface."""

from __future__ import annotations

from typing import Protocol


class GenericAgentAdapter(Protocol):
    def get_state(self) -> dict:
        ...

    def load_state(self, handoff: dict) -> None:
        ...

    def touched_files(self) -> list[str]:
        ...
