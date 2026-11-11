# Native allocator integration

The normal R1 composition now selects `r1/src/application/board/native_heap.c`
in place of upstream `heap_4.c`. Both units still compile; only the native
allocator participates in composition. No allocator C bodies changed in this
step. The stock allocator's 16-byte allocation header, caller tracking,
24-minus-low-three-bits size adjustment, and strict greater-than-32 split
threshold differ from the generic upstream allocator.

[Machine-readable evidence](native-heap-c-integration-review.json) binds the
selected sources, manifest, REA instruction evidence, probes, build and hybrid
reports by SHA-256. REA checked the locked malloc instructions and literals.

The selected native allocator and locked stock routines agree on 236 traces
containing 2,113 paired operations (4,226 executions). Each operation compares
the complete 51,200-byte heap, start sentinel, state and scheduler-boundary
observations. Coverage includes size/overflow/failure boundaries, fragmentation,
free permutations, initialization and null free. Root allocation callers use
the same return address, so caller words compare exactly. Three deliberate
mutations to size rounding, splitting and caller tracking are rejected.

A second comparison runs actual queue creation, reset/list initialization,
deletion and the actual selected allocator together: 64 traces and 400 paired
operations. Dynamic and static queues, four-live-queue free permutations and
reallocation agree. Active allocation caller words are checked against each
actual allocation-call return address, then normalized because C and stock
queue call sites differ. Other heap and queue bytes compare directly.
Scheduler suspend/resume and critical boundaries are modeled in both probes.
Fixed stock RAM placement is a probe fixture; production placement, malformed
heap behavior, physical concurrency and hardware execution remain unverified.

All 573 R1 units compile, with no failures or duplicate strong symbols.
Application imports fall from 187 to 186, resolving only
`r1_malloc_failed_hook`; bootloader imports remain 34. Allocator object bytes
are unchanged from the preceding report; this step changes provider selection.

Five compiler profiles produce no exact native allocator regions. The canonical
source plan is unchanged: 3,833 source-built bytes and 642,327 binary-pull-through
bytes, plus 248 resource bytes. The resulting hybrid still equals the locked
application byte for byte. This is neither a complete source rebuild nor proof
of allocator instruction identity. G2 corpus gates are unchanged.
