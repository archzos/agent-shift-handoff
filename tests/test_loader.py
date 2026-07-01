from __future__ import annotations

import pytest

from agent_shift_handoff.loader import load_handoff
from agent_shift_handoff.models import handoff_from_dict


class DummyAgent:
    def __init__(self) -> None:
        self.state = None

    def load_state(self, handoff: dict) -> None:
        self.state = handoff


def test_loader_injects_context(sample_payload):
    agent = DummyAgent()
    doc = handoff_from_dict(sample_payload)

    loaded = load_handoff(doc, agent)
    assert loaded["verification"].status in {"VALID", "DEGRADED"}
    assert agent.state is not None
    assert agent.state["task_goal"] == sample_payload["task"]["goal"]


def test_loader_rejects_invalid(sample_payload):
    agent = DummyAgent()
    payload = dict(sample_payload)
    payload["resume_instructions"] = {
        "first_actions": ["Continue working"],
        "verification_checks": [],
        "known_risks": [],
    }
    doc = handoff_from_dict(payload)

    with pytest.raises(ValueError):
        load_handoff(doc, agent)
