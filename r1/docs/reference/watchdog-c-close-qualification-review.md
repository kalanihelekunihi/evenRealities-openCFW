# Watchdog close adapter byte qualification

The existing C `r1_native_watchdog_hw_close` now supplies its complete 12-byte
native region at `0x500c8`: eight instruction bytes plus a four-byte cached
handle literal. Official qualification compiles and links that body at the
named stock entry with recovered bindings for the cached handle and registry
close dispatcher, then verifies every byte. No firmware source or manifest
was changed for this admission.

The hardware pass compiled 25 variants across five source units and recorded,
O2, Os, Oz and Og settings. It accepted the close adapter and independently
reconfirmed the existing feed thunk at `0x95be8`. The thunk was already in the
canonical plan, so its duplicate selection was skipped. Only the new official
12-byte close selection was appended; every existing plan unit remains intact.
The requested RTC driver had no candidate anchor in this pass and was not
compiled as a qualification candidate. Other tested bodies did not qualify.

All 120 stock/C integration comparisons pass. The actual close/feed wrappers
and registry dispatchers execute; only the final operation callbacks are
modeled. Cases include null cached devices, missing operations, two controlled
device records, varied callback results and cached-handle mutation during the
callback. Checks compare return value, callback identity/defined arguments,
controlled device/table/global storage, R4-R11, SP, interrupt masks and callback
alignment. Provider-private stack bytes and unrelated caller-saved residue are
not asserted. Physical watchdog operation and reset remain unverified.

The candidate-plan hybrid application retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Its plan hash matches the promoted canonical plan. Source-built content rises
from 3,649 to 3,661 bytes, with 642,499 retained bytes and 248 resource bytes.
That is hybrid equality, not a complete source-only rebuild.

The unchanged latest full R1 source report has 562 compiled units, no failures
or duplicate strong symbols, and 210 application / 34 bootloader imports.
Source checks pass. No G2 pseudocode gate changed. Exact source, compiler,
qualification, duplicate-selection, integration and hybrid bindings are in the
[machine-readable review](watchdog-c-close-qualification-review.json).
