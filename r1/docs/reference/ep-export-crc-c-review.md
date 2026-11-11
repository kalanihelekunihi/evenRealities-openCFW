# R1 EP export reader, CRC and length in C, 2026-11-11

`r1/src/application/runtime/native_ep_storage.c` now owns stock `0x5dff8`,
`0x5e060`, `0x5e086` and `0x5e0d8`. The record probe scans two EP sectors
for an eight-byte record whose low tag nibble is 10. The reader ensures EP
storage is initialized,
then delegates to the existing bounded EP read owner. The CRC routine first
checks the output pointer and ensures
EP storage is initialized. It allocates one 4,096-byte buffer, reads both EP
sectors in order, folds each admitted read into the existing stock CRC-32
implementation, then frees the buffer. The length getter advertises 8,192
bytes. The flash callback's status is ignored by the stock EP read wrapper;
the C path retains that behavior.

The ignored host probe under `build/r1-ep-export-crc-c-20261111/` compiles
the source with only ELF section tags removed for macOS, using ASan and
UBSan. It covers the reader's initialization gate, null CRC state, failed
initialization, failed allocation, both sectors, the record probe's early
exit, and ignored flash callback status. A Unicorn probe executes locked stock
`0x5dff8`, `0x5e060` and `0x5e086` with providers intercepted and verifies
the same gates and call order. Both pass.
The probes do not establish complete
export behavior or physical flash behavior.

`build/sources-r1-export-read-probe-c-20261111/report.json` compiles all 940
application and 82 bootloader units with zero failures or duplicate strong
symbols. `./make.sh sources-check` passes. The strict application receipt at
`build/r1-link-export-read-probe-c-20261111/report.json` still has 12 undefined
references and uses 644,640 of 696,320 flash bytes. The strict bootloader
receipt at `build/r1-boot-link-export-read-probe-c-20261111/report.json` links
with a valid vector. The later
[export command](export-command-c-review.md) binds these helpers into the
virtual-file path.
