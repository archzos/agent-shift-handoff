# agent-shift-handoff

[![CI](https://github.com/archzos/agent-shift-handoff/actions/workflows/ci.yml/badge.svg)](https://github.com/archzos/agent-shift-handoff/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

`agent-shift-handoff` generates structured shift handoffs for long-running
agents, verifies them at session start, and resumes work without replaying
already completed steps.

This is a session-continuity tool, not a memory-tier system.

## What it provides

- Versioned handoff schema
- Handoff generator with conservative continuity scoring
- Verifier that checks schema completeness and artifact drift
- Loader for resumed sessions
- SQLite state store for handoff history
- Streamlit dashboard for session continuity history

## Open-source boundaries

- Standalone OSS tool, not an archzOS platform dependency.
- Not affiliated with Anthropic or Letta.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest

python3 examples/coding_agent_session_1.py
python3 examples/verify_handoff.py
python3 examples/coding_agent_session_2.py
```

## Status

- Day 1 baseline complete: schema/model/store/tests + CI.
- Day 2 baseline complete: generator/verifier/loader/compactor + end-to-end example flow.
- Day 3 demo hardening pending: richer LangGraph live integration and polished dashboard broadcast asset.
