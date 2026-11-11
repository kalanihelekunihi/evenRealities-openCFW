# R1 GoMore sleep-interval update in C

`native_gomore_interval_update.c` implements the 130-byte native wrapper at
`0x5d370` in ordinary C. The [receipt](gomore-interval-update-c-review.json)
binds REA instructions/bytes, production source/object hashes, replay artifacts,
negative controls and build results. It reuses the authenticated context word
at `0x20007c4c`; no RAM or assembly is added.

The wrapper clears the current context's pending byte at offset 734 before
any provider call. A nonnull output is cleared for 56 bytes; null output still
runs the interval engine. A private 32-byte result is cleared, then the shared
context is reloaded for the engine arguments: context+4400, +400, +396, the
incoming mode and the result pointer. The engine's status is ignored. Output
receives two ordered word copies from result offsets 0 and 4, followed by four
byte copies from offsets 26–29 to offsets 8–11. The context is reloaded after
those stores. Unless its profile byte at offset 14757 is exactly 3, propagation
receives context+5112, the result pointer and a private scratch output. All
completed wrapper returns yield zero, including lower-provider errors.

REA confirms the propagation callee does not read its second argument and
only writes the scratch byte when enabled. No initial scratch value or native
private stack placement is required by this observed interface. The existing
provider-rich portable helper remains a distinct analysis API: its extra
validation and success/failure behavior cannot directly bind this native call.
The two lower native interfaces remain explicit dependencies rather than
being routed through incompatible convenience APIs.

Validation passed 2,328 direct stock/C pairs and another 2,328 pairs executing
the actual C EABI memory-clear wrapper and upstream musl memset. Each corpus
contains 400 matched faults and 1,928 completed returns. Cases cover null
output, mode extremes, all relevant profile branches, partial/failed engine
writes, output aliasing the pending/profile/context fields or context word,
and null/wrapped contexts. Each includes 160 provider-mutation configurations,
132 of which are reached. Context changes during output clear, result clear,
engine and propagation are observed at the native reload points.

Comparisons include provider arguments/order, result content, guarded output
and shared-cell bytes, full context-region hashes, ordered wrapper store
widths, faults, saved integer registers, SP, masks and FPSCR on completed
returns. Clear-internal write widths, private stack bytes and caller-clobbered
registers are excluded. Engine and propagation remain modeled providers;
physical/concurrent execution and final linking are not established.

Nine compiled defects were rejected: cached context, wrong result flag offset,
short output clear, wrong mode, wrong pending offset, wrong profile offset,
inverted propagation branch, omitted first word and wrong return status.

All 665 units compile, with successful application/bootloader relocatable
composition and no duplicate strong symbols. All 664 prior objects are
unchanged; the wake caller's declaration now records the recovered zero-return
interface. Resolving this wrapper exposes the native interval engine at
`0x7244e` and propagation at `0x7266a`, leaving 165 application and 34 bootloader
imports. This increase reflects the newly exposed call graph, not final-link
completion.

Instruction qualification rejects the wrapper's relocation pattern. The
canonical plan remains 4,369 source-built bytes, 641,791 executable pull-through
bytes and 248 resource bytes; a fresh hybrid application matches the locked
artifact through pull-through. A complete source-only link, complete context
initialization, byte-identical C reconstruction and hardware validation remain
unfinished.

The subsequent [propagation review](gomore-propagate-c-review.md) supplies
its C native interface and verifies this caller through the actual C packed
accessors and exact-one pending clear. The interval engine remains native.

The remaining interval engine now has a [native contract analysis](gomore-interval-engine-native-analysis.md),
including signed clamping and policy/output alias behavior. Its C native route
remains unresolved.

The [engine C review](gomore-interval-engine-c-review.md) now provides that native
interface and verifies this caller with its actual C engine and propagation.
