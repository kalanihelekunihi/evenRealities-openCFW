# R1 Bosch accelerometer configuration setter in C

The setter at stock `0x545CA` now uses C. It checks the device before the
configuration pointer, reads performance/bandwidth/ODR for validation in
stock order, then reloads the configuration for packing. It writes the range
byte to register `0x41` before the packed configuration byte to `0x40`.
If the second write runs, it updates cached performance mode from the
reloaded packed byte even when that write fails. REA confirms this sequence.
Compile-time assertions bind the four-byte configuration and cache offset.

All 3,075 comparisons pass: byte combinations and per-field full-byte sweeps,
independent checker/validator/write errors, null configuration, replacement
of input during validation and mutation of packed bytes during writes.
Tests compare ordered input reads, helper arguments, adjacent scratch
pointers, exact register bytes, cache updates, returned status and final
input. Mocks poison r0–r3; r4–r11, entry SP and callback eight-byte alignment
pass. A const volatile view preserves the final packed-byte reload without
making callback writes to the ordinary underlying array invalid.

The checker, validator and write boundary are explicit mocks. Validator
success for arbitrary byte combinations exercises packing and does not mean
those combinations are valid hardware settings. Physical configuration,
complete fault state, private spills, timing and byte identity remain open.
Scratch addresses and private stack depths are normalized or recorded
separately.

The setup source now contains no inline assembly. The enable and FIFO
configuration instruction bodies are unchanged from the preceding build.
All 561 R1 units compile and both compositions pass without duplicate strong
symbols, with unchanged 238/34 application/bootloader unresolved sets.
`make sources-check` passes for both device trees. No source-plan selection
or workflow gate changed.

[bma-c-accel-config-review.json](bma-c-accel-config-review.json) binds source,
build/native/candidate hashes, REA results and ignored probe artifacts under
`build/goal-r1-bma-accel-config/`.
