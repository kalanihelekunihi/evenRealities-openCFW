# R1 health sync acknowledgements in C, 2026-11-10

`r1/src/application/runtime/native_activity_sync_ack.c` now supplies four
stock callbacks from C: activity `0x3c0d8`, heart rate `0x3fcec`, HRV
`0x40bd4`, and SpO2 `0x43eb0`. The manifest retains one source unit for
these four functions. A shared C helper uses each callback's cursor index,
queue consumer, logging strings, and clock order. It preserves live mode
reads for the update logs after providers can mutate the context. HRV reads
its clock only for cursor modes; the other three sample it before reading
mode. All four retain null diagnostics, future-time rejection, monotonic
cursor updates, offline FIFO consumption and release of non-null contexts.

Ignored emulator probes under `build/r1-sync-ack-four-20261110/` compare the
pinned official application with the shared C object. **7,644 paired cases**
pass: 1,911 per callback. The cases cover null and unknown modes, future
and equal timestamps, cursor boundaries, all logging-bit combinations,
partial health-record reads, and mutations of mode or acknowledged time
during clock, record and logging provider calls. They compare provider order
and arguments, logging text, record bytes, payload memory, stack restoration,
saved registers and interrupt masks. Activity, HRV and SpO2 execute every
stock instruction start. The heart-rate body executes 107 of 108 disassembled
starts; the remaining `0x3fdfa` is trailing padding after the return. The
normal manifest object has identical allocated sections and relocation
records to the tested object. Provider internals are modeled, so the replay
does not establish physical flash, timekeeping or radio behavior.

The stable R1-only source build at
`build/sources-r1-four-sync-ack-stable-20261110/report.json`
compiles 887/887 application and 82/82 bootloader units with no known
failures or duplicate strong symbols. The strict bootloader links with a
valid vector. The strict application at
`build/sources-r1-four-sync-ack-stable-20261110/app-link/report.json` has **32
undefined symbols**, down from 36 before this callback group. Full flash
load overflow is **26,712 bytes**, 1,552 bytes above the checkpoint before
these four functions. The shared helper is about 644 allocated object bytes
smaller than four separate C implementations before final linker layout.
A complete application executable and byte identity remain unverified.

A repository-wide `make sources` run compiled every payload with no known
failures or duplicate strong symbols, then returned nonzero because source
and manifest inputs changed during the long G2 compilation. The shared
`make sources-check` passed afterward; the R1-only build above exited zero.
