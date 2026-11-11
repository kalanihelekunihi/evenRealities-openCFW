# R1 RTC device operations and native memory adapter

The existing RTC device unit and native memory-move adapter now participate
in relocatable composition. Their C and object bytes are unchanged from the
preceding snapshot repair. The 88-byte RTC record matches current locked
scatter output after normalizing its sole name reference, including the
RTC2 register address `0x40024000`, IRQ 36 and four-channel descriptor.

All 2,736 movement comparisons pass for ordinary RAM. They cover independent
source/destination alignments, equal pointers, both overlap directions,
disjoint ranges and lengths from zero through selected boundaries up to 512.
The linked C uses the existing pinned musl `memmove`/`memcpy` providers, not
a mocked copy. Buffer bytes and the unusual native r0 result match: source
on the backward-overlap path, destination end otherwise. SP and r4–r11 are
preserved. This is not access-order, MMIO or fault-equivalence proof.

Thirty calendar-write and twelve callback-binding comparisons also pass.
They cover controlled match/mismatch comparison results, aligned/unaligned
external calendar data, overlap with the RTC record, and storing/clearing raw
callback words. Calendar writes copy all 44 bytes verbatim; name mismatch
returns two and leaves the record untouched. Callback storage does not invoke
the callback. The comparison provider is mocked, while both copy primitives
are actually executed. Complete record/output bytes and return values match.

Together with the [snapshot ordering review](rtc-snapshot-order-review.md),
this checks the three exported device operations before composition. REA
observes 72-byte calendar-write, 84-byte callback-binding and 64-byte native
movement bodies at `0x563F8`, `0x56444` and `0x2775C`, respectively. The native
name-search loop exits after record zero; no full-table scan or new argument
guard was introduced.

All 562 R1 units compile and both compositions pass. The memory adapter import
resolves, reducing application imports from 239 to 238; bootloader imports
remain 34. No imports or duplicate strong symbols were added. The wider RTC
lifecycle/driver setup, epoch initialization and startup registration remain
separate work at that stage. The subsequent
[epoch review](rtc-epoch-review.md) verifies initialization without changing
its body; the later [lifecycle review](rtc-lifecycle-review.md) checks open,
driver-bridge arguments and registration. Physical driver execution remains separate.
No physical RTC operation, source-plan admission, canonical
coverage update or whole-image byte-identity claim follows from this closure.

[rtc-device-closure.json](rtc-device-closure.json) binds unchanged source and
object hashes, report identity, full comparison artifacts and REA evidence.
Probes remain under ignored `build/goal-r1-rtc-device/`.
