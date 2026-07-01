from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_shift_handoff.models import handoff_from_dict
from agent_shift_handoff.verifier import verify_handoff


def main() -> None:
    handoff_path = Path("handoffs/session_1_handoff.json")
    payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    document = handoff_from_dict(payload)
    result = verify_handoff(document, base_dir=Path("."))
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
