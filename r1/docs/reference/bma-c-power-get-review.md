# R1 Bosch power-save getter C conversion

`r1_bma4_get_advance_power_save` at stock `0x54408` now uses C. It initializes
its scratch byte to zero, invokes the device checker before checking the
output pointer, returns UINT32_MAX on either validation failure, then reads
one byte from register `0x7C`. Only a successful read updates the output with
bit zero; transport errors propagate unchanged. REA confirms this sequence.
The retained read boundary has an explicit four-argument declaration; its
instruction body and the other two functions in this unit remain unchanged.

All 2,064 modeled comparisons pass: every read byte, four transport statuses,
callbacks that write or leave scratch untouched, four checker results and
null/non-null output and device arguments. Checks cover call order/arguments,
initial scratch zero, output preservation on error, status, r4–r11 and entry
SP preservation, and callback eight-byte alignment. The checker and read
boundary are explicit mocks in the probe link; this does not validate their
actual implementations or a physical Bosch device. Private stack depths
differ and are recorded separately. No complete fault, timing or byte-identity
claim is made.

## Why the LIS route setter remains assembly

REA and 64 stock-only no-write probes confirm that the setter at `0x756DA`
seeds its two read buffers from incoming r3 and r2. If both reads return zero
without writing, those bytes influence the final register `0x3F` write.
The test sweep varies both incoming bytes and route bits and checks all four
read/write observations. A C rewrite that initializes those scratch bytes to
zero changes stock behavior; reading uninitialized C temporaries cannot
establish a portable replacement. The setter therefore stays unchanged while
other hardware work continues.

All 561 R1 units compile and both compositions pass with unchanged 238/34
application/bootloader unresolved sets and no duplicate strong symbols.
`make sources-check` passes for both trees. No source-plan selection or
workflow gate changed.

[bma-c-power-get-review.json](bma-c-power-get-review.json) binds source/build
hashes, native/candidate bytes, REA results, getter comparisons and retained
LIS setter observations. Probes remain under `build/goal-r1-bma-power/`.
