"""CLI for handoff generation, verification, and loading."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from agent_shift_handoff.adapters.langgraph_adapter import LangGraphAgentAdapter
from agent_shift_handoff.generator import MockHandoffClient, generate_handoff
from agent_shift_handoff.loader import load_handoff
from agent_shift_handoff.models import HandoffDocument, handoff_from_dict, handoff_to_dict
from agent_shift_handoff.report.store import fetch_latest_handoff
from agent_shift_handoff.state_store.sqlite_store import write_handoff
from agent_shift_handoff.verifier import verify_handoff


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-shift-handoff")
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate")
    generate.add_argument("--session-id", required=True)
    generate.add_argument("--agent", required=True)
    generate.add_argument("--state-db", required=True)
    generate.add_argument("--output", required=True)
    generate.add_argument("--dry-run", action="store_true")

    verify = sub.add_parser("verify")
    verify.add_argument("--handoff", required=True)
    verify.add_argument("--state-db", required=True)
    verify.add_argument("--dry-run", action="store_true")

    load = sub.add_parser("load")
    load.add_argument("--handoff", required=True)
    load.add_argument("--agent", required=True)
    load.add_argument("--state-db", required=True)
    load.add_argument("--dry-run", action="store_true")

    dashboard = sub.add_parser("dashboard")
    dashboard.add_argument("--db", default="state/sessions.sqlite")
    dashboard.add_argument("--serve", action="store_true")

    return parser


def _mock_state(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "agent_id": "langgraph-agent",
        "goal": "Implement a continuation-safe partial coding task",
        "status": "IN_PROGRESS",
        "completed_steps": ["Added function skeleton", "Wrote checksum helper"],
        "pending_steps": ["Implement verifier", "Wire loader"],
        "blocked_steps": [],
        "touched_files": ["agent_shift_handoff/schema.py", "agent_shift_handoff/verifier.py"],
        "checksums": {},
        "environment": {
            "tool_versions": {"python": "3.11"},
            "active_processes": [],
            "external_dependencies": [],
        },
        "decision_log": [
            {"decision": "Use SQLite", "rationale": "portable and session-local", "timestamp": "2026-07-01T12:00:00Z"}
        ],
        "open_questions": ["Should the next session regenerate the prompt template?"],
        "resume_instructions": {
            "first_actions": ["verify artifact checksums", "load the handoff", "continue implementing verifier"],
            "verification_checks": ["checksum matches", "handoff schema valid"],
            "known_risks": ["artifact drift"],
        },
        "continuity_score": 0.88,
    }


def _load_document(path: str) -> HandoffDocument:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return handoff_from_dict(payload)


def main() -> None:
    args = _build_parser().parse_args()
    if args.command == "generate":
        state = _mock_state(args.session_id)
        document = generate_handoff(state, client=MockHandoffClient())
        if not args.dry_run:
            write_handoff(args.state_db, document)
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(handoff_to_dict(document), indent=2), encoding="utf-8")
        print(json.dumps(handoff_to_dict(document), indent=2))
        return
    if args.command == "verify":
        document = _load_document(args.handoff)
        result = verify_handoff(document, base_dir=Path(args.handoff).parent)
        print(json.dumps(asdict(result), indent=2, default=str))
        return
    if args.command == "load":
        document = _load_document(args.handoff)
        adapter = LangGraphAgentAdapter()
        loaded = load_handoff(document, adapter, base_dir=Path(args.handoff).parent)
        if not args.dry_run:
            write_handoff(args.state_db, document)
        print(json.dumps({"loaded": True, "verification": asdict(loaded["verification"])}, indent=2, default=str))
        return
    if args.command == "dashboard":
        if args.serve:
            import subprocess
            import sys

            subprocess.run([sys.executable, "-m", "streamlit", "run", str(Path(__file__).parent / "report" / "dashboard.py"), "--", "--db", args.db], check=True)
            return
        latest = fetch_latest_handoff(args.db)
        print(json.dumps(latest, indent=2) if latest else "No handoffs found.")
