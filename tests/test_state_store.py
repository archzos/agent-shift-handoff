from __future__ import annotations

from pathlib import Path

from agent_shift_handoff.models import handoff_from_dict
from agent_shift_handoff.state_store.sqlite_store import add_note, get_handoff, list_handoffs, write_handoff


def test_state_store_write_and_get(tmp_path: Path, sample_payload):
    db_path = tmp_path / "sessions.sqlite"
    doc = handoff_from_dict(sample_payload)

    write_handoff(str(db_path), doc)
    loaded = get_handoff(str(db_path), doc.session_id)

    assert loaded is not None
    assert loaded["session_id"] == doc.session_id


def test_state_store_list_and_notes(tmp_path: Path, sample_payload):
    db_path = tmp_path / "sessions.sqlite"

    first_payload = dict(sample_payload)
    first_payload["produced_at"] = "2026-07-01T12:00:00+00:00"
    first = handoff_from_dict(first_payload)
    second_payload = dict(sample_payload)
    second_payload["session_id"] = "22222222-2222-2222-2222-222222222222"
    second_payload["produced_at"] = "2026-07-01T12:10:00+00:00"
    second = handoff_from_dict(second_payload)

    write_handoff(str(db_path), first)
    write_handoff(str(db_path), second)
    add_note(str(db_path), first.session_id, "compacted step notes", "2026-07-01T12:00:00+00:00")

    rows = list_handoffs(str(db_path))
    assert len(rows) == 2
    assert rows[0]["session_id"] == second.session_id
