from __future__ import annotations

from copy import deepcopy

import pytest
from jsonschema import ValidationError, validate

from agent_shift_handoff.schema import HANDOFF_SCHEMA


def test_schema_accepts_valid_document(sample_payload):
    validate(instance=sample_payload, schema=HANDOFF_SCHEMA)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda doc: doc.pop("task"),
        lambda doc: doc.__setitem__("continuity_score", "0.9"),
        lambda doc: doc["task"].__setitem__("status", "RUNNING"),
        lambda doc: doc["resume_instructions"].__setitem__("first_actions", []),
        lambda doc: doc["artifacts"][0].__setitem__("state", "UNKNOWN"),
    ],
)
def test_schema_rejects_invalid_documents(sample_payload, mutator):
    payload = deepcopy(sample_payload)
    mutator(payload)
    with pytest.raises(ValidationError):
        validate(instance=payload, schema=HANDOFF_SCHEMA)
