from __future__ import annotations

from typing import Any

from agent_shift_handoff.generator import generate_handoff


class AlwaysInvalidClient:
    def generate(self, prompt: str, state: dict[str, Any]) -> dict[str, Any]:
        return {"schema_version": "1.0"}


def test_generate_handoff_returns_valid_document(sample_payload):
    doc = generate_handoff(sample_payload)
    assert doc.session_id == sample_payload["session_id"]
    assert 0.0 <= doc.continuity_score <= 1.0
    assert doc.resume_instructions.first_actions


def test_generate_handoff_degrades_after_retries(sample_payload):
    doc = generate_handoff(sample_payload, client=AlwaysInvalidClient(), retries=1)
    assert doc.continuity_score <= 0.5
    assert doc.raw_state.get("degraded") is True
    assert "generation_error" in doc.raw_state
