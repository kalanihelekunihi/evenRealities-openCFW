# R1 LIS2DW12 FIFO burst C conversion

`r1_lis2dw12_fifo_burst_read` now uses C instead of a naked assembly body.
Stock at `0x750A0` multiplies the incoming sample count by six, takes the low
16 bits, and reads register `0x28` through `lis2dw12_read_reg`. The C uses
unsigned multiplication and an explicit `uint16_t` conversion, preserving
wraparound rather than clamping the transfer. REA confirms this stock call
shape; the instruction sequence establishes the unsigned-width behavior.

All 665 modeled callback comparisons pass: 560 burst cases cover counts
0–127, 10921–10923, 32767–32768, 65534–65536 and selected 32-bit extrema,
with four callback return values. Another 105 cases execute the FIFO caller
through level detection and the converted burst. Checks compare callback
identity, handle, register, destination, transfer length, return value and
destination data. Callback mocks poison caller-saved argument registers;
callee-saved r4–r7 and entry SP are preserved.

The compiled wrapper is 30 bytes versus stock's 24. The compiler inlines the
transport and tail-calls its callback; callback stack depths differ from
stock and are recorded separately. Private stack contents, complete fault
state, timing and byte identity are not established. The FIFO caller and
register-level assembly remain unchanged in this snapshot. The subsequent
[FIFO reader conversion](lis-c-fifo-review.md) replaces the caller separately.
These tests do not exercise a
physical accelerometer or I2C controller.

All 561 R1 units compile and both compositions succeed without duplicate
strong symbols. Application/bootloader unresolved sets remain 238/34.
`make sources-check` passes for both device trees. No source-plan selection
or workflow gate changed.

[lis-c-burst-review.json](lis-c-burst-review.json) binds source/object/native
bytes, the successful report, matrix, REA evidence and ignored probe hashes
under `build/goal-r1-lis-burst/`.
