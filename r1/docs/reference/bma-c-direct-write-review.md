# R1 Bosch direct register-write driver in C

The driver at stock `0x9756A` now uses C with the pinned Bosch callback types
and compile-time context-offset checks. It validates the device before the
data pointer, clears register bit seven for interface zero, captures the bus
write callback then handle, and stores the signed callback result in context
byte nine. A bus error returns -2 without delay. Success reloads performance
mode, delay callback and handle, calls delay with 2 microseconds only for
mode one (450 otherwise), then returns zero. REA confirms this ordering.

All 3,392 comparisons pass. They cover every byte register, interface values
0/1/255, canonical signed-byte callback results 0/1/-1/-128, performance
values 0/1/2/255, zero through full-width lengths, absent callbacks and null
device/data pointers. Mutation cases replace the delay function and handle
and change performance mode during the bus callback. Exact ordered context
reads/writes, callback arguments, status and final context match stock.
The caller's data remains untouched. Callback mocks poison r0–r3; r4–r11,
entry SP and eight-byte callback alignment pass.

The normal compiled device checker runs in the probe; only bus write and
delay are mocked. Large lengths are forwarded without actually dereferencing
their entire range. No DMA, physical transfer or elapsed-delay claim is made.
Tests use the byte register and signed-byte callback ABI; unspecified upper
bits outside that ABI are not a portable C contract.

The compiled body is 88 bytes versus stock's 90. The other six function
bodies in this unit retain their previous instruction bytes. Private stack,
complete fault state, timing and byte identity remain unproven. The separate
write-boundary assembly and the hardware divide pair remain.

All 561 R1 units compile and both compositions pass without duplicate strong
symbols, with unchanged 238/34 application/bootloader unresolved sets.
`make sources-check` passes for both device trees. No source-plan selection
or workflow gate changed.

[bma-c-direct-write-review.json](bma-c-direct-write-review.json) binds source,
checker/header/build hashes, native/candidate bytes, REA data and ignored
probe artifacts under `build/goal-r1-bma-direct-write/`.
