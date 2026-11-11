# R1 stream unregistration in C

`r1/src/application/runtime/native_stream_unregister.c` supplies the name wrapper
at `0x89b08` (88 contiguous instruction bytes) and object removal at `0x89c20`
(218 bytes). [The machine-readable review](stream-unregister-c-review.json)
retains REA assembly and pinned byte receipts, source/build hashes, replay
results and limits. The inventory's larger wrapper range includes shared
continuations; deferred cleanup at `0x89ba8` remains solely implemented in
`native_stream_cleanup.c`. A supplemental frontier row identifies the separate
object entry without changing the existing inventory size.

## Recovered behavior

The wrapper looks up the object by name. A found object is passed to the object
body with the original handle. Missing objects use the stock short-circuit
logging-mode calls, tags and messages. No new null-name guard is introduced.

The object body enters the existing architectural fault adapter for a null
object or zero handle. It walks the object's listener list and compares full
pointer words with the supplied handle. A matching listener during active
dispatch is marked through its halfword at offset twenty; then the fresh object
flag byte is ORed with pending bit four. No unlink/free occurs on this path.

Outside active dispatch, the listener is unlinked and freed before list emptiness
is queried. An empty list frees a nonzero buffer and then clears buffer/used
fields. A zero buffer leaves used bytes unchanged. The fresh context is passed
to object stop. A surviving list instead transfers to rate reduction. The
existing C implementations supply both lower paths.

A missing handle leaves the list intact and emits the native diagnostic when
selected, using handle plus four and the object name as string arguments. The
root does not validate those string pointers before forwarding them. Tests
compare diagnostic calls and arguments; actual formatter failure behavior for
invalid pointers is outside this fixture.

Both recovered interfaces are void, matching the existing factory consumer.
Caller-clobbered R0/flags are not promoted into synthetic return-value APIs.

## Verification

The primary fixture passes 1,290 paired native/C cases, comparing provider order,
arguments, final object/listener/buffer state, guards, ordered watched accesses,
normal return SP, masks and callee-saved registers. It covers empty through
three-node lists, first/middle/last/missing handles, immediate and deferred
paths, null guards, logging combinations, full-word handles, object/listener
aliases, random mark words and 256 seeded provider-mutation sequences. Freed
records are poisoned. Lookup, list primitives, unlink/empty, free, stop, rate
reduction, diagnostics and fault boundaries are modeled in that direct set.

Another 120 paired cases execute actual native/C list primitives, unlink,
object stop, rate reduction, sample conversion and timer-period setters. Another
80 start at actual factory shutdown and reach the new wrapper/body and those
providers, with either the aging or accelerometer subscription populated and
with/without a mode timer. Lookup, allocator/free, timer release, memory move,
logging and fault boundaries remain modeled. Driver tables are absent in those
integration cases. Linked provider hashes are recorded.

The integration fixtures disable memory observers for the documented Unicorn
list-head IT observer issue. They compare call boundaries and final state,
including resized buffers, period words and factory state. Ordered-access claims
come from the primary fixture. Six compiled negative controls are rejected:
wrong dispatch bit, wrong listener mark, wrong pending bit, skipped unlink,
wrong stop context and changed logging short-circuit behavior.

Primary call-depth sets match: wrapper lookup at sixteen bytes, object list/free
and diagnostics at twenty-four, and stop/rate/SDK diagnostic tails at zero.
The fixture asserts native/C depth-set equality. The existing factory-shutdown
eight-byte frame gap remains in the compound path. Private stack words,
caller-clobbered registers and APSR are excluded. Fault comparison ends before
the BASEPRI/store gateway; physical exceptions and asynchronous scheduling are
not established. This is a tested behavior candidate, not proof of complete ABI,
instruction or physical equivalence.

## Build status

`make sources-check` passes. All 618 units compile (544 application and 74
bootloader); both relocatable compositions pass without failures or duplicate
strong symbols. All preceding 617 objects are identical. The manifest adds only
the unregistration unit. Its import resolves without exposing another, leaving
167 application and 34 bootloader imports. The wrapper frontier row is updated,
and only the object-entry supplemental row is added.

Scoped qualification compiles the unit but rejects both anchored relocation
patterns and admits zero bytes. The canonical source plan is unchanged. The
fresh hybrid matches locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
using 4,271 source-built bytes, 641,889 executable pull-through bytes and 248
resource bytes. A complete source-only link, candidate byte identity, real
allocator/timer/driver integration and physical sensor behavior remain open.

Reports: `build/sources-goal-r1-stream-unregister-c/report.json` and
`build/hybrid-goal-r1-stream-unregister-c/build-report.json`. Fixtures and audits
remain under `build/goal-r1-stream-unregister-c/`; durable receipts are in the
JSON review above.
