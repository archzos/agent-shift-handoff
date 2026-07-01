# Failure Modes

## Artifact drift

The filesystem changed between sessions. The verifier flags the affected
artifact and the resumed session must account for the change.

## Lossy generation

The handoff omits important file paths, decisions, or pending steps. The
continuity score should drop and the verifier marks the handoff degraded.

## Brittle resume instructions

The first actions are vague or non-executable. The verifier rejects the
handoff as invalid.

## Missing environment state

Tool versions or active processes are not recorded. The resumed session may
reconstruct the wrong context.
