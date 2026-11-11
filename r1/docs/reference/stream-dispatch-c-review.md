# R1 native stream timer dispatcher in C

`r1/src/application/runtime/native_stream_dispatch.c` supplies
`r1_stream_timer_dispatch` at native entry `0x8a1e0`. Its first argument is the
timer record; word 12 supplies the stream object. It is not the generic vendor
candidate's `(framework, timer)` interface. Registration's declaration now
reflects that argument. This declaration change leaves its object identical.

The contiguous dispatcher occupies 304 bytes through `0x8a30f`. The inventory's
422-byte function includes the separate 118-byte shared cleanup continuation
at `0x89ba8`. REA's assembly returns both ranges; the cleanup implementation is
not claimed by this C candidate. Its tail transition remains the unresolved
`r1_stream_deferred_cleanup(object)` provider. That continuation walks and frees
marked listeners, clears object flag four, and either releases an empty object's
buffer before its stop helper or invokes the remaining-list retiming helper.
Those deeper operations require separate validation before implementation.

## Recovered behavior

The dispatcher guards the object, provider/read callback, sample buffer, byte
rate and halfword sample width. A stale cursor at or beyond `rate * width` is
reset. The provider receives buffer plus cursor, current width and object
context. Width is reread after the provider returns; a mismatch ends dispatch.
On success the cursor wraps only on exact chunk equality. The delivered sample
base uses the fresh buffer pointer. Object active flag two is set before the
listener walk and cleared afterward; pending flag four requests cleanup.

Listener flag bit zero suppresses delivery. Mode one delivers a sample directly
at equal rates, otherwise updating the 15-bit accumulator packed above that bit.
Mode zero delivers only at a wrap. An equal-rate batch uses the current buffer;
a differing-rate batch invokes the existing sample converter into buffer plus
chunk and reloads the callback afterward. Both batch lengths are truncated to
16 bits, including the converter's return value. Other modes are skipped. The
next-list operation runs after each callback, observing callback-driven changes.

## Validation and limits

[The machine-readable review](stream-dispatch-c-review.json) records stock REA
receipts, the source object, build audit and replay results. REA pseudocode failed
with a Ghidra address-space range error; assembly and byte readback succeeded.
Readback was compared with the locked application rather than trusting the
provider's memory view alone. The CLI doctor was also run; its shell-environment
Java/configuration diagnostics do not establish the cause of the remote
decompilation failure. No tool installation or configuration was changed.

The initial 243 native-only probes established the timer-record ABI, callback
argument order, cursor behavior, batch truncation and cleanup tail entry. The
final fixture passes 1,289 paired native/C cases (these include the original
243 cases, not an additional count). Cases include all mode classes, equal and
differing rates, 40,000-byte widths, stale cursors, short reads, guard exits,
accumulator overflow, pending cleanup, one to three listeners and subscriber
mutations of object width/rate/buffer/flags and listener flags.

The fixture compares provider call order and arguments, final object and
listener state, and ordered reads/writes of watched timer, provider, object and
listener fields. Narrow store values are masked to the actual access width:
Unicorn reports the full source register even when STRH only stores its low
16 bits. This does not assert source-register identity. List, converter,
read/subscriber and cleanup boundaries are modeled; neither physical sensors nor
asynchronous interrupts are exercised. Provider callbacks clobber caller-saved
registers. Return SP and callee-saved registers are checked, while private stack,
APSR and caller-saved register identity are excluded.

Five compiled negative controls are rejected: untruncated converted-batch length,
wrong cleanup flag, retained active bit, wrong per-sample mode and discarded
accumulator history. Source replay cannot fall through to stock instructions.
The native dispatcher frame is 40 bytes versus 48 for C at ordinary providers;
both restore the caller frame before deferred cleanup. Full stack and byte
identity are unproven.

## Build status

`make sources-check` passes. All 611 units compile (537 application, 74 bootloader),
and both relocatable compositions pass without failures or duplicate strong
symbols. All preceding 610 objects remain identical. Only the dispatcher unit
was added to the manifest. It resolves `r1_stream_timer_dispatch` and exposes
`r1_stream_deferred_cleanup`, leaving 169 application and 34 bootloader imports.

Scoped qualification compiles the candidate but admits no bytes. The canonical
source plan is unchanged. A fresh hybrid matches locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
using 4,271 source-built bytes, 641,889 executable pull-through bytes and 248
resource bytes. This is not a complete source-only firmware link. Physical
sensor delivery, cleanup integration, the architectural zero-divisor dependency
and candidate byte identity remain open.

Reports: `build/sources-goal-r1-stream-dispatch-final-c/report.json` and
`build/hybrid-goal-r1-stream-dispatch-c/build-report.json`. Experiments and
replay/negative-control scripts remain under
`build/goal-r1-stream-dispatch-contract/`; their durable receipts are in the JSON
review above.

The subsequent [cleanup and object-stop candidate](stream-cleanup-c-review.md)
resolves the deferred-cleanup import and supplies its empty-list stop path.
Another 340 paired cases execute the actual dispatcher, cleanup, stop and list
providers together. The dispatch frame difference remains; the surviving-list
rate-reduction helper is now explicit, leaving application imports at 169.
