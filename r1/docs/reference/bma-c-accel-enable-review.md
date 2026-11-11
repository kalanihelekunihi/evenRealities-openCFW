# R1 Bosch accelerometer-enable setter in C

The setter at stock `0x54640` now uses C. It initializes a scratch byte,
validates the device and reads register `0x7D`. Successful reads pass through
the existing Bosch C bit-update helper and write the result back. The delay
callback is then reloaded from context offset 44, followed by the handle at
offset four, and called with 25,000 microseconds. This happens even if the
write failed; the write status is preserved across the delay callback.
Validation or read errors skip both write and delay. REA confirms this order.

All 2,220 comparisons pass. Tests cover every register byte, enable inputs
0/1/2/255/256/UINT32_MAX, independent checker/read/write errors, untouched read
buffers and callback/handle changes during write. Null devices are tested
with rejection statuses, matching the real checker's contract; a mock that
accepts null would violate that contract. Ordered calls, scratch-byte
initialization, exact written byte, final status, r4–r11, entry SP and
eight-byte callback alignment are checked. Mocks poison r0–r3, including the
delay return, to verify the write status survives. Callback stack depths
also match in this compiled candidate.

The actual C bit-update helper runs; checker, read/write boundaries and delay
are explicit mocks. No physical sensor enable, bus operation or elapsed delay
is validated. The candidate is 88 bytes versus stock's 78. Full fault state,
private spills, timing and byte identity remain unproven. The other two
setup functions retain their assembly instruction bytes.

All 561 R1 units compile and both compositions pass without duplicate strong
symbols, with unchanged 238/34 application/bootloader unresolved sets.
`make sources-check` passes for both device trees. No source-plan selection
or workflow gate changed.

[bma-c-accel-enable-review.json](bma-c-accel-enable-review.json) binds source,
helper/build/native/candidate hashes, REA results and ignored probe artifacts
under `build/goal-r1-bma-enable/`.
