# R1 native heart-rate workspace and resource getters in C

The [graph dispatch review](goodix-graph-dispatch-c-review.md) supersedes the single dispatch boundary with C dispatch and mode0/1/2 wrappers. Full HR lifecycles now allocate mode0/1 records through C; the deeper graph initializer and mode6 constructor remain modeled.

The workspace initializer (`0x72c48`), pair-buffer helper (`0x667c6`), filter descriptor initializer (`0x92848`) and four resource getters now use C in `r1/src/application/goodix/native_hba_workspace.c`. The [receipt](goodix-hba-workspace-c-review.json) pins REA reads, normal/tested objects, sources, fixtures and results.

Workspace setup clears 344 bytes and creates nine filter records in native order, nine short queues and seven float records. Eight short queues have capacity 180; slot seven has capacity 60. The native `ceil` input is the exact binary64 integer 60.0, and the unsigned conversion returns 60. This caller-specific constant is folded in C; the generic math implementation remains unchanged.

The pair helper allocates with the full wrapping half-count but initializes with its low byte. The descriptor preserves padding, stores the coefficient pointer before clearing state, writes the state pointer afterward and returns the end pointer. No allocation checks or cleanup were added. The prior inventory's 52-byte helper size overlapped the next version function; fresh control flow establishes a 30-byte body ending in a tail branch. The next function's inventory row is unchanged.

Canonical readonly model-data views supply all four resource getters and the filter coefficients. All 64,252 graph-resource bytes plus 80 coefficient bytes match their stock spans. No second resource definition is added. The first candidate composition rejected a duplicate coefficient symbol; the successful final implementation reuses the existing view, and all final tests were rerun against it.

All 477 paired comparisons pass with independent workspace, queue/filter, allocation and zero-state oracles. Every one of the 440 native instruction bytes executes. Only allocation is modeled in these direct comparisons; existing C queue/memory primitives execute. Cases cover full-width count allocation, low-byte initialization, ignored float arguments, null allocation results, untouched bytes, allocator mutations and active floating-point state. Twenty-two compiled defects are rejected.

All 128 complete HR constructor/real-allocator/teardown lifecycles pass with workspace and resource getters executing in C. All primary, workspace, filter, graph and queue allocations coalesce to the prior heap top. Graph records are preallocated using each real allocator and transferred through modeled graph returns; graph construction internals and allocation timing remain unproven. Resource pointers are normalized only in comparison output and graph-provider traces, never rewritten during execution. All resource bytes remain unchanged.

The final 887-unit build passes without duplicate strong symbols. The tested object equals the normal object; 876 prior nongenerated source/object pairs are unchanged. Five imports are removed: application imports fall from 78 to 73 and boot imports remain 22. No writable state or resource definitions are added; source-plan and cache layout are unchanged.

Logical null-state write faults do not establish physical access width or fault delivery. Invalid pointers, concurrency, cold floating-point activation, future graph cursor bounds, numerical inference, final executable linking/startup and boot remain open. This is an `ld -r` composition, not a bootable firmware image. Byte identity is waived for this goal.
