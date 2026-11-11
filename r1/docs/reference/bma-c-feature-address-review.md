# R1 Bosch feature-address controls in C

Feature-address reset at stock `0x8EDD8` and increment at `0x70FDA` now use
C. Reset validates the device, writes register `0x5B` from context byte 23,
then register `0x5C` from byte 24 if the first write succeeds. It passes the
original field pointers, preserving observations of changes between writes.
Increment initializes both scratch bytes, reads those registers in order,
uses the existing Bosch C address helper, then writes the updated bytes in
order. Either read failure maps to -2; checker and write statuses propagate.
REA confirms these control-flow and pointer contracts.

All 3,952 controlled comparisons pass. Reset covers every low byte, high-byte
extremes, changes to the second context byte during the first write, and
independent checker/write errors. Increment covers nibble carry, wide and odd
transfer lengths, 12-bit address wraparound, every low and high byte in boundary
sweeps, callbacks that leave scratch untouched and independent errors at all
five operation stages. Tests compare complete ordered call traces, numeric
context pointers for reset, scratch identity within each increment, bytes
written, returned statuses and context changes. Mocks poison r0–r3; r4–r11,
entry SP and eight-byte callback alignment pass.

The normal compiled address helper runs in the candidate. Checker and direct
register operations are explicit mocks, so physical feature-memory access
and bus behavior remain unverified. Scratch addresses are normalized by role
between images; private stack depths differ for increment. Complete fault
state, private spill contents, timing and byte identity remain open. The
remaining functions in both touched source units retain their instruction
bytes; direct transfer declarations now spell out the four-argument ABI.

All 561 R1 units compile and both compositions pass without duplicate strong
symbols, with unchanged unresolved sets of 238 application/34 bootloader.
`make sources-check` passes for both trees. No source-plan selection or
workflow gate changed.

[bma-c-feature-address-review.json](bma-c-feature-address-review.json) binds
source/helper/build hashes, candidate/native bytes, REA results and ignored
probe hashes under `build/goal-r1-bma-address/`.
