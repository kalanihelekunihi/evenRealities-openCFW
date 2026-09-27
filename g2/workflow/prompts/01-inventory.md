# P1 worker: artifact and image inventory

Objective: map only the assigned authenticated container/image scope and return
evidence for the global inventory. This is analysis preparation, not C work.

Verify the locked hashes before parsing. Inspect the approved parser/tool
behavior before execution; reject tools that rebuild, modify, or launch agents
as a side effect. Parse the assigned container, validate lengths/checksums and
enumerate every child record/image. Write offset/address maps, transform
descriptions, architecture/ISA/endian evidence, entry/vector facts, and initial
code/data/container/padding/unknown intervals. Preserve undecided ranges as
unknown. Capture external ROM/hardware dependencies separately.

Compare relevant old manifests and corpora to actual files and byte hashes.
List reusable evidence with its scope and missing prerequisites. Conflicting
prose or counts are findings, not reasons to choose the easier denominator.
Do not start decompilation in an inventory-only assignment, write C, or design
implementation modules.

Required outputs: image/mapping records, interval ledger, nested-image list,
evidence-reuse assessment, receipts and task result. Acceptance requires exact
range conservation within assigned container scope, explicit child mappings,
verified parser boundaries, and no silently omitted contents. G1 may retain
explicit code/data unknowns for P2; it never proves complete pseudocode.
