# Respiratory clear-two C investigation

This is the pre-integration checkpoint. The subsequent [C review](gomore-clear-two-c-review.md) records consolidation and production-object replay.

Stock `0x883d4` (26 bytes) clears twenty bytes at record, then twenty at record+20.
The experimental C routine preserves that order and tail-calls the second EABI
clear. The [receipt](gomore-clear-two-c-investigation.json) binds REA bytes,
source/object, direct/fault replay, defects and respiratory integration.
No production source or manifest changes at this checkpoint.

**2,056 native/C cases**, including **seven faults**, pass. Cases include all 256
initial byte patterns at eight alignments, invalid pointers and RAM-end partial
writes. **2,048 guarded cases** have independent forty-byte expectations.
Provider arguments and SP depths match exactly: eight bytes below entry at the
first clear, restored entry SP at the second. Partial byte-write order, fault
address/size, surrounding bytes, registers and completed SP agree. Raw R0 also
matches for this selected compiled void routine; it is not a portable C return
contract. Stock EABI byte clearing executes on both paths.

Five compiled variants are rejected: short first/second length, shifted second
destination, reversed calls and a merged forty-byte call. The last two are
rejected for native call-order/shape and provider-SP differences, rather than
necessarily differing final valid-buffer bytes. Compilation failures do not count.

The respiratory C root passes **2,792 native/C cases** with this C clear helper
linked. It also passes those cases with the existing production C history and
three statistics helpers linked together. Optical estimation remains modeled;
software FP, square root and underlying EABI byte clear execute natively. Exact
estimator scratch pointers and the 96-byte respiratory frame remain checked.
The integrated helper object hashes are recorded in the results.

The generic clear-two API has null/length guards and bool result. Consolidate it
as a checked wrapper around the native operation when promoting respiratory
update; do not duplicate a stock implementation. Production-object build/replay,
qualification and the proposed coordinator frame correction are still pending.
Physical behavior, a full source-only graph/final link and byte identity remain
unproven. Experiments are under `build/goal-r1-gomore-clear-two-c/`; the normal
build remains 687 units with 179 application and 34 bootloader imports.
