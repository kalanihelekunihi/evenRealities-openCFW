# Heart-rate, SpO2 and HRV RAM cache merges in C, 2026-11-10

`r1/src/application/runtime/native_short_ram_cache_merge.c` supplies the
stock heart-rate, SpO2 and HRV RAM merges at `0x3fef4`, `0x440c4` and
`0x40de0`, plus their timestamp clamps at `0x3f9dc`, `0x43bd4` and `0x408b8`.
A shared C helper selects each source-owned daily cache accessor, builder
reset, packet flush, row width and logging strings. It preserves the 24
hourly slots, the special final slot, live cache timestamp and offset reads,
byte-sized output count, future-time clamp, logging modes, and restoration
of the builder flag after flush. The manifest unit uses `-Oz` and contains
no assembly.

An ignored paired replay under `build/r1-health-cache-merge-20261110/`
compares the SHA-pinned official 2.2.6.0009 application with the C object.
**5,535 paired cases** pass, 1,845 for each merge. They cover zero and future windows, sparse and
dense cache rows, all eight logging-mode values, UTC-provider mutation of the
cache day, logging-provider mutation on the stale-day path, and reset/flush
provider mutations. Provider call order and arguments, log text, cache and
builder bytes, saved registers and stack restoration agree. All **509 of 509**
stock instruction starts in the three merge and clamp pairs execute across the
cases (169 heart-rate, 169 SpO2, 171 HRV). The manifest object has the same
allocated sections and 64 relocation records as the replayed `-Oz` object.
The shared object has 1,610 allocated bytes, 632 fewer than three separate
replayed objects before final linking. Provider internals are modeled, so this
does not establish physical timekeeping, cache placement or transport behavior.

The R1-only source build at
`build/sources-r1-short-ram-merges-20261110/report.json` compiles 888/888
application and 82/82 bootloader units with no known failures or duplicate
strong symbols. The strict bootloader links with a valid vector. The strict
application at
`build/sources-r1-short-ram-merges-20261110/app-link/report.json`
has **29 undefined functions**, three fewer than before these merges. The full
flash load exceeds its configured span by **27,840 bytes**, 1,128 bytes more
than the preceding 32-import checkpoint. A complete application executable and byte
identity remain unverified.
