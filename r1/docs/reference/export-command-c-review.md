# R1 virtual log export command and preparation in C, 2026-11-11

`r1/src/application/runtime/native_export_snapshot_prepare.c` owns the stock
descriptor at `0x20006918` and its prepare callback at `0x58de4`. The
descriptor points to the source-owned prepare, read, start, and finish
callbacks and to the separate snapshot start-sector byte. Preparation pauses
EP persistence, counts populated log sectors, finds the sector after the
first erased sector, computes CRC over EP/log/cache/crash content in stock
order, and publishes length/checksum to the caller and descriptor. On a
failed EP-only admission or first allocation, it clears the export guards.
The [read callback review](export-snapshot-read-c-review.md) covers the
virtual-file ranges.

`r1/src/application/runtime/native_export_command.c` owns stock `0x4e740`
and its cold command state at `0x20006c28`. It sends the ten-byte start
reply through the existing EUS fragmenter, sets fast BLE mode, waits 50 ms
between control and data sends, streams at most 4,096 bytes per command
through the existing PB fragmenter, advances the offset, and invokes the
descriptor's finish callback on completion or cancellation.

The ignored host probes under `build/r1-export-prepare-c-20261111/` and
`build/r1-export-command-c-20261111/` compile the C bodies with ASan and
UBSan. They cover rotating sectors, CRC and descriptor updates, cache
allocation failure, rejected preparation, two data chunks, completion,
cancellation, and failed chunk allocation. Unicorn probes execute the locked
stock `0x58de4` and `0x4e740` bodies with external providers intercepted.
They verify the same sector rotation, CRC, descriptor fields, command packet
bytes, provider order, chunk lengths, offset changes, and cleanup. The stock
prepare probe caught an off-by-one: scanning starts after the first erased
sector. The C implementation was corrected and both probes pass.

`build/sources-r1-export-command-c-20261111/report.json` compiles 942/942
application and 82/82 bootloader units without failures or duplicate strong
symbols. The strict application receipt at
`build/r1-link-export-command-c-20261111/report.json` has 11 undefined
functions and uses 647,608 of 696,320 flash bytes, with no flash overflow.
The strict bootloader receipt at
`build/r1-boot-link-export-command-c-20261111/report.json` links with a
valid vector. `./make.sh sources-check` passes. Live BLE delivery, concurrent
flash writes, physical device behavior, and byte identity remain unverified.
