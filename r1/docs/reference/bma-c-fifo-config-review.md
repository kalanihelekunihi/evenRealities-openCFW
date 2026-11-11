# R1 Bosch FIFO configuration setter in C

The setter at stock `0x546D0` now uses C. It zeroes both scratch bytes,
validates the device and reads two bytes from register `0x48`. The existing
Bosch C helper updates the selected bits. It writes the low byte to `0x48`,
then, only on success, reloads the delay callback and handle, calls delay
with 1,000 microseconds and writes the high byte to `0x49`. The second write
uses the next byte of the original scratch pair. The first failure stops
the sequence and its status propagates. REA confirms this order.

All 3,746 comparisons pass. They cover all configuration masks, every low
and high register byte in boundary sweeps, enable values beyond zero/one,
independent errors at each stage and all four partial-read masks. Mutation
cases change the delay callback/handle during the first write and the exposed
high scratch byte during delay. Ordered calls, exact written bytes, adjacent
scratch pointers and returned status match stock. Mocks poison r0–r3;
r4–r11, entry SP and eight-byte callback alignment pass.

The actual C bit helper runs; checker, register reads/writes and delay are
explicit mocks. This does not validate physical FIFO configuration or
elapsed delay. Private stack depths are recorded separately, and complete
fault state, private spills, timing and byte identity remain unproven.
The accelerometer-enable and accelerometer-configuration function instruction
bodies are unchanged; the latter still retains assembly.

All 561 R1 units compile and both compositions pass without duplicate strong
symbols, with unchanged 238/34 application/bootloader unresolved sets.
`make sources-check` passes for both trees. No source-plan selection or
workflow gate changed.

[bma-c-fifo-config-review.json](bma-c-fifo-config-review.json) binds source,
helper/build/native/candidate hashes, REA results and ignored probe artifacts
under `build/goal-r1-bma-fifo-config/`.
