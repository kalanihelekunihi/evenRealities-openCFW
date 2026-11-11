# R1 sleep storage iterator in C, 2026-11-11

The source-owned iterator at stock application `0x5b39c` is
`r1/src/application/runtime/native_sleep_sync_iterator.c`. It snapshots the
sector count, scans eight 24-byte headers per sector, reads at most 232 data
bytes through the sleep FAL device, checks the Modbus CRC, and passes each
valid record and its flash header address to the existing report callback.
Mode one skips records already marked `0x11223344`. A null callback,
allocation failure, or CRC mismatch returns zero; a callback stop or complete
scan returns one. CRC failure publishes event `0x2002` before freeing the
buffer. Read results are ignored and the header is zeroed once, preserving
the stock behavior for partial FAL reads.

The ignored host probe at `build/r1-sleep-iterator-c-20261111/` uses a
generated copy of the C source with only the FAL read and 32-bit partition
pointer replaced by host mocks. It exercises null callback, allocation
failure, ordinary records, synchronized-record skip, callback stop, CRC
failure/event, oversized record, and a second sector. ASan and UBSan pass.
The mock does not validate physical FAL behavior or instruction identity.

`build/sources-r1-sleep-iterator-c-20261111/report.json` compiles all
939 application and 82 bootloader units with no known failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-sleep-iterator-c-20261111/report.json` has 12 unresolved
functions, one fewer than the prior checkpoint, and reports 644,624 of
696,320 flash bytes used without overflow. The strict bootloader receipt at
`build/r1-boot-link-sleep-iterator-c-20261111/report.json` links with a
valid vector. The R1 source manifest check passes.
