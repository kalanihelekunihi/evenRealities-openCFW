# R1 structured-log cache read helpers in C, 2026-11-11

`r1/src/application/board/structured_cache_copy.c` now owns the stock
availability check at `0x41d08`, its count tail at `0x91490`, and the read
wrapper at `0x91460`. The count validates the two cursors against capacity,
computes wrapped occupancy, and returns its low 16 bits. The read wrapper
copies without consuming the read cursor. With the `all` argument set it
snapshots available bytes and writes that length to the caller's halfword;
otherwise it uses the caller's supplied halfword length.

The ignored host probe under `build/r1-cache-read-c-20261111/` compiles the
actual C source with ASan and UBSan. It covers explicit and whole-cache
reads, wraparound, cursor preservation, invalid cursors, 16-bit narrowing and
null arguments. The Unicorn probe executes the three stock functions from
the locked 2.2.6.0009 application for wrapped occupancy, argument order,
length updates and invalid cursors. Both probes pass. These tests isolate the
cache helpers; they do not validate a complete log export.

`build/sources-r1-cache-read-c-20261111/report.json` compiles all 939
application and 82 bootloader units without failures or duplicate strong
symbols. `./make.sh sources-check` passes. The strict application receipt at
`build/r1-link-cache-read-c-20261111/report.json` still has 12 undefined
references and uses 644,640 of 696,320 flash bytes. The strict bootloader
receipt at `build/r1-boot-link-cache-read-c-20261111/report.json` links with
a valid vector. The export prepare/read callbacks and command still need
source owners before the virtual file is usable.
