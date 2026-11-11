# R1 Bosch write-control function in C

The write-control function at stock `0x5475A` now uses C. It checks the device
before the input pointer and forwards ordinary registers directly. For
register `0x5E`, it obtains the saved power byte and disables power saving
only when that byte is one and the getter succeeded. It rejects odd/excessive
lengths or failed power setup with -10, then selects direct or chunked
transfer using the live chunk limit. A successful transfer restores power
saving only when the reloaded byte is exactly one. REA confirms the extra
getter-status condition that distinguishes this path from read control.

All 1,791 comparisons pass: ordinary/feature registers, zero/odd/boundary/
full-width lengths, feature/chunk limits, power values, independent helper
errors, null input, changes to context limits and changes through a retained
scratch-byte pointer. Complete ordered helper calls and context-limit reads,
write payloads, status and final context match stock. Input bytes remain
unchanged. Mocks poison r0–r3; r4–r11, entry SP and callback eight-byte
alignment pass. The scratch byte is ordinary storage accessed through a
const volatile view for stock-required reloads.

All helper entry points are explicit mocks in this review. No physical bus,
power state or elapsed delay is tested. Large lengths are passed to a bounded
dry mock. Private stack depths differ; complete fault state, private spills,
timing and byte identity remain unproven.

The other six functions in the feature-I/O source retain their previous
instruction bytes. This source now has no naked assembly functions; only
the hardware divide pair remains inline assembly. All 561 R1 units compile,
both compositions pass without duplicate strong symbols, and unresolved
sets remain 238 application/34 bootloader. `make sources-check` passes for
both device trees. No source-plan selection or workflow gate changed.

[bma-c-write-control-review.json](bma-c-write-control-review.json) binds
source/build/native/candidate hashes, REA data and ignored probe artifacts
under `build/goal-r1-bma-write-control/`.
