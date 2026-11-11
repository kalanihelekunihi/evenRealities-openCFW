# R1 export snapshot reader in C, 2026-11-11

`r1/src/application/runtime/native_export_snapshot_read.c` owns the stock
`0x592bc` virtual-file read callback. It traverses the EP, circular log flash,
structured-log cache, and retained crash-text ranges. It uses the existing
source-owned EP reader, FAL log pointers, cache peek reader, and reset-trace
text pointer. Its snapshot start-sector byte and cache-length halfword are
separate from the live log writer's sector byte. The locked stock RW decoder
shows the start-sector byte cold-initialized to `0xff`; the C owner starts at
`-1` and is intended to be set by snapshot preparation.

The ignored host probe under `build/r1-export-read-c-20261111/` compiles the
actual callback body with ASan and UBSan. It covers EP/log and
log/cache/crash crossings, short reads, ignored FAL status, null/zero input,
failed EP read, unset start sector, failed cache allocation, and out-of-range
offsets. A Unicorn probe executes locked stock `0x592bc` for both crossings
and verifies returned bytes and provider order. That stock comparison exposed
the distinction between the snapshot start sector at `0x20006905` and live
writer sector at `0x20006907`; the C owner now uses the former. Both probes
pass. Success-path diagnostic logging and wider malformed-state cases remain
for the final callback audit.

`native_retained_log.c` also owns the stock text pointer and string-length
getters at `0x7f018` and `0x7f024`, reusing the canonical reset-trace buffer.
The later [descriptor and command implementation](export-command-c-review.md)
connects this reader to the BLE export path.

`build/sources-r1-export-read-probe-c-20261111/report.json` compiles 940/940
application and 82/82 bootloader units, with no failures or duplicate strong
symbols. The strict application receipt at
`build/r1-link-export-read-probe-c-20261111/report.json` retains 12
undefined functions and uses 644,640 of 696,320 flash bytes. The bootloader
receipt at `build/r1-boot-link-export-read-probe-c-20261111/report.json`
links with a valid vector. `./make.sh sources-check` passes.
