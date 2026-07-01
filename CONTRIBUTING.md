# Contributing to agent-shift-handoff

This project focuses on reproducible session continuity, so changes should
prioritize correctness and verification.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## Workflow

1. Branch from `main`.
2. Keep changes focused.
3. Add or update tests.
4. Run `pytest` locally.
5. Call out any generator or verifier implications.

## Code style

- Prefer explicit dataclasses and typed state.
- Keep the schema versioned and stable.
- Make resume instructions actionable.
