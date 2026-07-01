from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_shift_handoff.generator import MockHandoffClient, generate_handoff
from agent_shift_handoff.models import handoff_to_dict
from agent_shift_handoff.state_store.sqlite_store import write_handoff


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    workdir = Path("examples/workspace")
    handoff_dir = Path("handoffs")
    state_db = Path("state/sessions.sqlite")
    workdir.mkdir(parents=True, exist_ok=True)
    handoff_dir.mkdir(parents=True, exist_ok=True)

    artifact = workdir / "calculator.py"
    artifact.write_text(
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n\n"
        "def subtract(a: int, b: int) -> int:\n"
        "    # TODO: implement in session 2\n"
        "    raise NotImplementedError\n",
        encoding="utf-8",
    )

    checksum = sha256_file(artifact)
    state = {
        "session_id": "session-1",
        "agent_id": "langgraph:examples/coding_agent_session_1.py",
        "goal": "Build a tiny calculator module",
        "status": "IN_PROGRESS",
        "completed_steps": ["Created calculator module", "Implemented add()"],
        "pending_steps": ["Implement subtract()", "Add unit tests for subtract()"],
        "blocked_steps": [],
        "touched_files": [str(artifact)],
        "checksums": {str(artifact): checksum},
        "environment": {
            "tool_versions": {"python": "3.11"},
            "active_processes": [],
            "external_dependencies": [],
        },
        "decision_log": [
            {
                "decision": "Use explicit type hints",
                "rationale": "keeps resume session deterministic",
                "timestamp": "2026-07-01T12:00:00Z",
            }
        ],
        "open_questions": ["Should subtract() clamp negative outputs?"],
        "resume_instructions": {
            "first_actions": [f"Verify {artifact} checksum equals {checksum}"],
            "verification_checks": ["schema_valid", "artifact_checksum_match"],
            "known_risks": ["artifact drift before resume"],
        },
        "continuity_score": 0.84,
    }

    document = generate_handoff(state, client=MockHandoffClient())
    write_handoff(str(state_db), document)

    output_path = handoff_dir / "session_1_handoff.json"
    output_path.write_text(json.dumps(handoff_to_dict(document), indent=2), encoding="utf-8")
    print(f"Wrote handoff: {output_path}")


if __name__ == "__main__":
    main()
