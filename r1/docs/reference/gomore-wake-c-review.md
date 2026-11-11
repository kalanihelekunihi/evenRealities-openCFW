# R1 native Gomore sleep wake control flow in C

`native_gomore_wake.c` supplies stock entry `0x6b50c` (318 bytes). It reconstructs
the allocation, forced interval update, authorization, diagnostics, output setup
and ownership decisions. [The review receipt](gomore-wake-c-review.json) binds
production source/object hashes, REA bytes, startup initialization and replays.
No assembly or executable payload is introduced by this unit.

The function allocates and clears a 56-byte sensor record, then calls the native
interval updater with operation 1. A live authorization flag bit 0 requests
operation 4/state 0 through the native authorization interface. Diagnostics read
the live record fields. After logging, a fresh sensor flag bit 3 determines
whether output processing runs; provider changes during logs remain visible.

The output path initializes a count word and clears an 88-byte workspace,
allocates and clears 2,880 payload bytes, stores that pointer at workspace+8,
and calls the native interval dispatcher and final record publisher with the
count/workspace pointers. Count remains at workspace+88. Both lower calls run
even when the produced count is zero. The original payload pointer is freed
regardless of changes to its workspace copy, then the sensor record is freed.
Both allocation-failure paths preserve stock's diagnostics and cleanup choices.

The unit owns only the authenticated byte at `0x20006e04`, whose cold RW value
is 4. Executed startup handlers, independent RW decoding and poisoned-region
guards confirm that value and the compiled initial byte. Adjacent configuration
fields remain unowned.

Four lower calls remain explicit native dependencies: interval update `0x5d370`,
authorization dispatch `0x49410`, interval output dispatch `0x67bbc` and final
record publication `0x4a704`. Their frontier routes now identify the observed
native interfaces. The existing provider-rich Gomore analysis-plan APIs have
different signatures and are not substituted as executable providers.

There are 1,104 paired stock/C cases covering both allocation failures, sensor
and authorization flag combinations, all logging bits, changing log sequences,
interrupt masks, zero/large output counts, changed record fields and workspace
pointer replacement. They compare provider calls/arguments/order, heap and live
flag snapshots, known output bytes, final allocation/free state, preserved
registers, SP and masks. Another 48 pairs execute the actual C memory-clear
bridge and `memset`; lower interval/output and allocation providers remain
modeled. Eight compiled defects are rejected: short sensor/workspace clearing,
wrong authorization/output bits, wrong payload size, skipping empty publication,
freeing a replaced pointer and omitting sensor cleanup.

The output workspace is native SP-120 versus C SP-112; count remains 88 bytes
after its base. This preserves the tested data interface, not pointer-address
identity. Ordinary provider call depths match at 120 bytes, while native
sensor-free tail paths are not reproduced by C. Private padding, raw void
return, caller-clobbered registers and flags are excluded. Physical wake,
concurrent mutation and complete lower-provider behavior remain unverified.

All 625 units compile and both relocatable payloads compose without duplicate
strong symbols. All 624 prior objects are unchanged. Resolving the wake entry
exposes four lower native calls, so application imports rise from 164 to 167;
bootloader imports remain 34. This is a more explicit native dependency graph,
not completion of those lower functions. Exact qualification rejects the new
body. The canonical plan is unchanged; a fresh hybrid retains 4,295 source-built
bytes and locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
A full source-only link and instruction identity remain open.

The [subsequent interval dispatcher review](gomore-dispatch-c-review.md) now
supplies that lower controller in C, exposing its selector and packed-output
interfaces separately.

The subsequent [interval-update review](gomore-interval-update-c-review.md)
replaces the wake path's native interval wrapper with C, exposing its two
lower native dependencies without changing the compiled wake caller.
