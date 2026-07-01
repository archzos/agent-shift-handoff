"""Handoff document verification."""

from __future__ import annotations

import hashlib
from pathlib import Path

from jsonschema import ValidationError, validate

from agent_shift_handoff.models import HandoffDocument, VerificationResult, handoff_to_dict
from agent_shift_handoff.schema import HANDOFF_SCHEMA


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _is_actionable(action: str) -> bool:
    lowered = action.strip().lower()
    if not lowered:
        return False
    if lowered in {"continue working", "resume", "keep going"}:
        return False
    tokens = lowered.split()
    if len(tokens) < 2:
        return False
    return True


def verify_handoff(document: HandoffDocument, base_dir: str | Path = ".") -> VerificationResult:
    issues: list[str] = []
    artifact_drifts: list[str] = []

    try:
        validate(instance=handoff_to_dict(document), schema=HANDOFF_SCHEMA)
    except ValidationError as exc:
        return VerificationResult(status="INVALID", issues=[f"schema:{exc.message}"], artifact_drifts=[])

    for artifact in document.artifacts:
        path = Path(base_dir) / artifact.path
        if not path.exists():
            artifact_drifts.append(f"missing:{artifact.path}")
            continue
        if artifact.checksum and _sha256(path) != artifact.checksum:
            artifact_drifts.append(f"checksum_mismatch:{artifact.path}")

    if document.continuity_score < 0.7:
        issues.append("continuity_score_below_threshold")

    first_actions = document.resume_instructions.first_actions
    if not first_actions:
        return VerificationResult(status="INVALID", issues=issues + ["invalid_resume_instruction"], artifact_drifts=artifact_drifts)
    if not _is_actionable(first_actions[0]):
        return VerificationResult(status="INVALID", issues=issues + ["invalid_resume_instruction"], artifact_drifts=artifact_drifts)
    if not any(keyword in first_actions[0].lower() for keyword in ("verify", "check", "validate", "compare")):
        return VerificationResult(
            status="INVALID",
            issues=issues + ["first_action_must_be_verification"],
            artifact_drifts=artifact_drifts,
        )

    status = "VALID"
    if issues or artifact_drifts:
        status = "DEGRADED"
    return VerificationResult(status=status, issues=issues, artifact_drifts=artifact_drifts)
