"""agent-shift-handoff package metadata and public exports."""

from agent_shift_handoff.models import (
    ArtifactState,
    DecisionEntry,
    EnvironmentState,
    HandoffDocument,
    ResumeInstructions,
    TaskState,
    VerificationResult,
    handoff_from_dict,
    handoff_to_dict,
)

__version__ = "0.1.0"

__all__ = [
    "ArtifactState",
    "DecisionEntry",
    "EnvironmentState",
    "HandoffDocument",
    "ResumeInstructions",
    "TaskState",
    "VerificationResult",
    "handoff_from_dict",
    "handoff_to_dict",
]
