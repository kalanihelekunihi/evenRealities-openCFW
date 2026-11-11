# Named GPIO initialization frame

The named-input initializer now supplies its C kernel with the native saved
R1/R2/R3 words. A 10-byte ABI bridge preserves stock's 32-byte frame. The
kernel puts the pin at entry SP minus 32, executes Nordic's port decoder and
writes PIN_CNF = 2, then builds the full four-byte configuration word at entry
SP minus 28. Sense and pull replace its first two bytes in native order.
Incoming R3 at entry SP minus 24 remains intact. Missing/already-open returns
preserve all three incoming words.

Raw instructions at stock `0x54b90` establish the frame and SDK call sequence.
The C initializer continues to ignore GPIOTE initialization statuses, reload
pin/configuration after provider calls, enable events and mark the record
opened, as stock does. This replaces the previous scalar pin-release helper
and compiler-owned configuration local, which did not preserve native returned
R1/R2/R3 or the provider-visible configuration address. The C constant template
is not a claim of reproducing stock's flash-template read/fault behavior.

All 2,960 initializer stock/C comparisons pass. Coverage includes seven records
and a missing name, opened values, pins across both ports, initialized states,
zero/nonzero SDK results, varied sense/pull bytes, mutation of configuration
fields during GPIOTE init, and mutation of configuration/pin during input init.
Checks include returned R0-R3, exact configuration pointer and four bytes,
registered IRQ callback role, callback-visible record state, final GPIO register
memory, name-read order, R4-R11, SP, interrupt masks and call alignment.
The old source independently reproduces the returned-register mismatch.

The previous callback/read/close probe also passes all 375 cases on this build.
All 562 R1 units compile without failures or duplicate strong symbols; imports
remain 211 application / 34 bootloader. The other 561 units are unchanged and
source checks pass. strcmp and SDK calls are modeled; port decoding and GPIO
register accesses execute against emulator memory. Physical electrical/IRQ
behavior, complete fault/concurrency equivalence, byte identity and final
source-only firmware remain unproven. Source-plan selections and G2 gates are
unchanged. Exact bindings are in the
[machine-readable review](named-gpio-c-open-frame-review.json).
