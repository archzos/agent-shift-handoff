from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_shift_handoff.models import handoff_from_dict


@pytest.fixture
def sample_payload() -> dict:
    return {
        "schema_version": "1.0",
        "session_id": "11111111-1111-1111-1111-111111111111",
        "agent_id": "langgraph-agent",
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "task": {
            "goal": "Implement verifier",
            "status": "IN_PROGRESS",
            "completed_steps": ["Added checksum helper"],
            "pending_steps": ["Implement file drift check"],
            "blocked_steps": [],
        },
        "artifacts": [
            {
                "path": "README.md",
                "state": "MODIFIED",
                "checksum": "",
                "notes": "doc updates",
            }
        ],
        "environment": {
            "tool_versions": {"python": "3.11"},
            "active_processes": [],
            "external_dependencies": [],
        },
        "decision_log": [
            {
                "decision": "Use SQLite",
                "rationale": "portable session-local store",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "open_questions": ["Should we support optional checksum for deleted files?"],
        "resume_instructions": {
            "first_actions": ["Verify README.md checksum and repository state"],
            "verification_checks": ["schema_valid", "artifact_drift_scan"],
            "known_risks": ["artifact drift"],
        },
        "continuity_score": 0.86,
    }


@pytest.fixture
def sample_document(sample_payload):
    return handoff_from_dict(sample_payload)
