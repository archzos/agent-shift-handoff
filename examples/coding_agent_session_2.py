from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_shift_handoff.loader import load_handoff
from agent_shift_handoff.models import handoff_from_dict


class DemoAgent:
    def __init__(self) -> None:
        self.loaded = None

    def load_state(self, handoff: dict) -> None:
        self.loaded = handoff


def main() -> None:
    handoff_path = Path("handoffs/session_1_handoff.json")
    artifact = Path("examples/workspace/calculator.py")
    payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    document = handoff_from_dict(payload)

    agent = DemoAgent()
    loaded = load_handoff(document, agent, base_dir=Path("."))
    print(f"Verification status: {loaded['verification'].status}")

    source = artifact.read_text(encoding="utf-8")
    source = source.replace(
        "def subtract(a: int, b: int) -> int:\n    # TODO: implement in session 2\n    raise NotImplementedError\n",
        "def subtract(a: int, b: int) -> int:\n    return a - b\n",
    )
    artifact.write_text(source, encoding="utf-8")
    print(f"Resumed and finished implementation in {artifact}")


if __name__ == "__main__":
    main()
