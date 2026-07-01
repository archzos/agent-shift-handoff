from __future__ import annotations

import hashlib
from pathlib import Path

from agent_shift_handoff.models import handoff_from_dict
from agent_shift_handoff.verifier import verify_handoff


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_verifier_valid_document(tmp_path: Path, sample_payload):
    file_path = tmp_path / "target.txt"
    file_path.write_text("hello", encoding="utf-8")

    payload = dict(sample_payload)
    payload["artifacts"] = [
        {
            "path": "target.txt",
            "state": "MODIFIED",
            "checksum": _sha256_text("hello"),
            "notes": "verified",
        }
    ]
    doc = handoff_from_dict(payload)

    result = verify_handoff(doc, base_dir=tmp_path)
    assert result.status == "VALID"
    assert not result.issues
    assert not result.artifact_drifts


def test_verifier_degraded_on_drift_and_low_score(tmp_path: Path, sample_payload):
    (tmp_path / "target.txt").write_text("changed", encoding="utf-8")

    payload = dict(sample_payload)
    payload["continuity_score"] = 0.2
    payload["artifacts"] = [
        {
            "path": "target.txt",
            "state": "MODIFIED",
            "checksum": _sha256_text("original"),
            "notes": "stale checksum",
        }
    ]
    doc = handoff_from_dict(payload)

    result = verify_handoff(doc, base_dir=tmp_path)
    assert result.status == "DEGRADED"
    assert "continuity_score_below_threshold" in result.issues
    assert result.artifact_drifts


def test_verifier_invalid_on_non_verification_first_action(sample_payload):
    payload = dict(sample_payload)
    payload["resume_instructions"] = {
        "first_actions": ["Continue coding"],
        "verification_checks": [],
        "known_risks": [],
    }
    doc = handoff_from_dict(payload)

    result = verify_handoff(doc)
    assert result.status == "INVALID"
    assert "first_action_must_be_verification" in result.issues or "invalid_resume_instruction" in result.issues
