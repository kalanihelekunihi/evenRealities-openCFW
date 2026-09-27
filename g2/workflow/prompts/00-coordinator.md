# Coordinator startup prompt

Prepare to execute the next user-authorized stage of the G2 pseudocode-first
campaign. Read `AGENTS.md`, `g2/workflow/README.md`, `PROCEDURE.md`, `CONTRACTS.md`,
`target.json`, `state.json`, and the prompt index. If the current user request is
still preparation only, inspect or improve these materials and stop without
launching analysis or reconstruction workers.

When the user requests decompilation, begin P1. Authenticate the original whole
bundle and all six payloads against the fixed target. Preserve the current dirty
tree and record actual input hashes. Create a new isolated campaign. Do not
resume the old runner or inherit the old incremental queue's task ownership.

Implement and verify the record/coverage/gate checks specified by the procedure
before dispatch. Keep one canonical inventory and one writer for task leases,
shared analysis facts, reviews and gate status. A state flag alone is not a gate.
Do not claim a parser, validator or scheduler exists unless you have verified it.

Build the whole-artifact inventory first, including all nested images, external
boundaries and address maps. Reuse historical evidence only after validating its
artifact identity, scope and tool provenance. Then dispatch bounded pseudocode
analysis assignments with `common.md`, the appropriate phase prompt, and a
filled task contract. Configure each parallel worker as `gpt-6-luna` with
reasoning effort `low`; start with a small calibration batch. Private output
ownership and immutable inputs are mandatory.

Have independent workers review submissions. Reconcile whole-artifact coverage,
including code that the original function inventory missed. No component may
start C work early. Do not create C task IDs, module partitions, C interfaces or
implementation assignments before G3. Generic prepared templates are the only
post-freeze materials allowed before that gate.

After full pseudocode review, collect G3 evidence and preserve an immutable,
durable corpus snapshot. Report that milestone and its limitations. Advance to
P4 only within the user's authorized scope and only if the whole-corpus gate
validates; a request limited to decompilation ends at the frozen corpus.

When C work is authorized and G3 passes, derive contracts and a dependency graph
from the corpus, complete G4, then use the later prompts. Invalidate the freeze
and park affected work if new semantic or coverage gaps appear. Integrate
accepted changes serially; never use new target pins or donor patches to make
comparison pass.

Maintain a concise campaign status with current phase, artifact/corpus IDs,
per-component coverage, unresolved findings, next eligible work and exact gate
evidence. Keep distinct claims for pseudocode completeness, source completeness,
component equality and whole-bundle equality. The final objective requires all
of them, not a percentage from the legacy queue.
