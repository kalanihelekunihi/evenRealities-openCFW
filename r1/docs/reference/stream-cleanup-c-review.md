# R1 deferred stream cleanup and object stop in C

`r1/src/application/runtime/native_stream_cleanup.c` supplies the shared cleanup
continuation at `0x89ba8` (118 bytes) and object stop at `0x8a180` (42 bytes).
The [machine-readable review](stream-cleanup-c-review.json) retains REA assembly
and byte receipts, validation, integration and build audit results. These entries
are supplemental frontier rows; the existing dispatch inventory includes the
shared cleanup range. Existing inventory rows remain unchanged and in order.

## Behavior recovered from stock

Cleanup returns zero for a null object. It captures each next-list pointer before
reading the current listener's low mark byte. Marked listeners are unlinked and
freed; traversal uses the captured next pointer, including after free poisons the
old record. It clears object flag four, then asks whether the list is empty.

For an empty list, a nonzero buffer is freed before clearing buffer and used-byte
fields. A zero buffer leaves the used-byte field unchanged. Context is loaded
fresh and passed to object stop. If listeners remain, cleanup restores its
caller frame and transfers to the unresolved `r1_stream_object_rate_reduce` at
`0x8a068`. Rate reduction scans remaining listener rates and may shrink the
buffer and retime the stream; its allocation, conversion and logging path still
requires implementation and validation.

Object stop captures its context argument, releases a nonzero timer using the
existing timer-release provider, then clears the object's timer pointer. It
rereads the provider table afterward. A stop callback receives the captured
context through a tail call, and its result is returned. A missing object or
provider returns zero; a provider with no stop callback returns the provider
pointer, preserving the stock R0 result. Cleanup's dispatch declaration was
updated to the recovered return type; its compiled object is unchanged.

## Verification

The primary fixture passes 2,151 paired native/C cases. It covers zero through
three listeners, low/high-byte mark combinations, null objects, provider and
callback presence, buffer and timer presence, arbitrary stop contexts, mask
state, late mark changes during next lookup and 256 seeded provider-mutation
sequences. It compares provider ordering and arguments, R0 results, final object,
listener and buffer state, guards, ordered watched field accesses, return SP,
callee-saved registers and masks. Freed listener records are poisoned. Narrow
store values are masked to their written width. All list/free/timer-release/
rate-reduction/callback boundaries are modeled in this direct fixture.

Another 1,892 paired cases execute actual native/C list head, next, empty and
unlink providers. Another 340 execute the actual dispatcher, cleanup, stop and
list providers together, including subscriber-requested deferred removal. These
integration fixtures compare call boundaries and final state. They model free,
timer release, rate reduction and external callbacks; the dispatcher fixture
also models the sensor read. Actual linked provider object hashes are recorded.

The list integration fixture disables memory observers. With its bounded memory
observer enabled, Unicorn 2.1.4 skips a move following the C list-head IT load
and later faults on a stale node register; the observer-free run passes. The
reproducing fixture and log remain under `build/goal-r1-stream-cleanup-c/`.
No production source was changed to accommodate that observation. Ordered memory
access claims apply to the direct fixture, while actual-list internals are
checked through call boundaries and final state.

Five compiled negative controls are rejected: reading the wrong mark byte,
clearing the wrong pending flag, discarding the stop context, clearing used bytes
without a buffer, and clearing the timer before its release callback.

Cleanup provider depths match at 24 bytes; object stop calls timer release at
16 bytes and tail-calls its callback at zero bytes. The direct fixture asserts
native/C depth-set equality. The prior dispatcher frame gap remains 40 native
versus 48 C bytes at read/subscriber callbacks. Private stack words,
caller-clobbered registers and APSR are excluded. No full instruction, private
frame, asynchronous interrupt or physical hardware identity is established.

## Build and remaining gates

`make sources-check` passes. All 612 units compile (538 application and 74
bootloader); both relocatable compositions pass without failures or duplicate
strong symbols. All preceding 611 objects are identical. The manifest adds only
the cleanup unit. The cleanup import resolves and rate reduction becomes
explicit, leaving 169 application and 34 bootloader imports.

Scoped qualification compiles the unit and rejects both anchored relocation
patterns; zero bytes are admitted. The canonical source plan is unchanged. A
fresh hybrid matches application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,271 source-built bytes, 641,889 executable pull-through bytes and 248
resource bytes. A complete source-only link, candidate byte identity, actual
timer-release integration and physical sensor delivery remain unproven. The
architectural zero-divisor provider also remains unresolved.

Reports: `build/sources-goal-r1-stream-cleanup-c/report.json` and
`build/hybrid-goal-r1-stream-cleanup-c/build-report.json`. Fixtures and audits
remain under `build/goal-r1-stream-cleanup-c/`; durable receipts are in the JSON
review above.

The subsequent [stream rate reducer](stream-rate-reduce-c-review.md) supplies
`r1_stream_object_rate_reduce`. Another 768 paired cases execute actual cleanup,
stop, rate reduction, list head/next/empty, sample conversion and timer-period
providers together. Raw SDK logging-result forwarding and architectural
zero-divisor behavior remain explicit; application imports remain 169.
