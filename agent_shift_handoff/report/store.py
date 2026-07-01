"""SQLite persistence for handoff documents."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from agent_shift_handoff.models import HandoffDocument, handoff_to_dict


def initialize_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS handoffs (
                session_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                produced_at TEXT NOT NULL,
                continuity_score REAL NOT NULL,
                document_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                session_id TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def write_handoff(db_path: str, document: HandoffDocument) -> None:
    initialize_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM handoffs WHERE session_id = ?", (document.session_id,))
        conn.execute(
            "INSERT INTO handoffs VALUES (?, ?, ?, ?, ?)",
            (
                document.session_id,
                document.agent_id,
                document.produced_at,
                document.continuity_score,
                json.dumps(handoff_to_dict(document, include_internal=True)),
            ),
        )


def fetch_latest_handoff(db_path: str) -> dict[str, object] | None:
    initialize_db(db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT document_json FROM handoffs ORDER BY produced_at DESC LIMIT 1"
        ).fetchone()
    return json.loads(row[0]) if row else None


def fetch_dashboard_payload(db_path: str) -> dict[str, object]:
    initialize_db(db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT session_id, agent_id, produced_at, continuity_score FROM handoffs ORDER BY produced_at DESC"
        ).fetchall()
    return {
        "handoffs": [
            {"session_id": row[0], "agent_id": row[1], "produced_at": row[2], "continuity_score": row[3]}
            for row in rows
        ]
    }


def add_note(db_path: str, session_id: str, note: str, created_at: str) -> None:
    initialize_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO notes VALUES (?, ?, ?)", (session_id, note, created_at))
