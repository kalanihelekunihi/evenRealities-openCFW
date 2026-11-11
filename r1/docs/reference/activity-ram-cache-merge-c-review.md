# Activity RAM cache merge in C, 2026-11-10

`r1/src/application/runtime/native_activity_ram_cache_merge.c` reconstructs
the activity daily RAM merge at stock `0x3c304`, its pending counter delta
accessor at `0x48d48`, and the future timestamp clamp at `0x3bcf8`.
The C path preserves the 144 ten-minute slots, 12/10/10-bit packed cache
fields, current-slot pending deltas, packet builder layout, live cache day and
UTC offset reads, logging modes, timestamp clamp, and builder flag restoration.
It reuses the source-owned activity cache, accumulator, builder reset and
packet flush providers. The manifest unit uses `-Oz` and contains no assembly.

An ignored paired Unicorn replay under
`build/r1-health-cache-merge-20261110/verify-activity.py` compares the
SHA-pinned official 2.2.6.0009 application with the C candidate. **1,312
paired cases pass**, including zero/future windows, sparse/dense cache slots,
all eight logging-mode values, active/inactive counter deltas, UTC-provider
mutation of the cache day, and logging-mode mutation on the stale-day path.
The compared outputs are provider calls and arguments, log text, cache and
builder bytes, accumulator state, saved registers and stack restoration.
The cases execute all **219 of 219** stock instruction starts across the
three functions. The manifest object has exactly the same allocated section
contents (928 bytes) and 33 relocation records as the replayed `-Oz` object.
Provider internals are modeled; these comparisons do not establish physical
cache placement, concurrent counter behavior, transport behavior, hardware
boot, or byte identity.

The R1-only build at
`build/sources-r1-activity-ram-merge-20261110/report.json` compiles 889/889
application and 82/82 bootloader units with no known failures or duplicate
strong symbols. The strict bootloader link is vector-valid. The strict
application report at
`build/sources-r1-activity-ram-merge-20261110/app-link/report.json` has
**28 undefined functions**, one fewer than the preceding checkpoint. The
full flash load exceeds its configured span by **28,712 bytes**, an increase
of 872 bytes. A complete application executable has not yet been linked.
