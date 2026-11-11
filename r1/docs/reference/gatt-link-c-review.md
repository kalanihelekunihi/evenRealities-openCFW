# R1 GATT disconnect link reset in C

The linked `native_gatt_observer.c` unit now supplies
`r1_sdk_gatt_link_init`, corresponding to stock `0x74f20`. The SDK's private
helper was inaccessible after its compilation unit was excluded for duplicate
event handling. The disconnect path can now call the linked C provider.

The eight-byte link receives six ordered writes: desired MTU 247, effective
MTU 23, pending/requested flags zero, desired data length 251 and effective data
length 27. The first two writes are halfwords; the rest are bytes. Compile-time
assertions pin all field offsets and size. Desired data length 251 comes from
stock instructions, independently of the historical SDK configuration seed's
27. No shared configuration value was changed.

REA/Ghidra read the complete helper and the native disconnect call site.
The production helper matches all 24 stock code bytes, with no relocations.
The official `qualify_sources.py` selected that body through anchored and unique
pattern checks; its emitted source plan deduplicates the two observations into
one region. Only that emitted 24-byte selection was added to the canonical plan,
after checking it does not overlap existing selections and validating the merged
hybrid build. The helper contains no executable inline assembly.

There are 1,536 direct stock/C comparisons over seeded RAM, aligned target
locations, incoming flags and both PRIMASK settings. They check the six writes'
order, widths and values, surrounding guards, untouched stack, R0/R1/R2/R3/R12,
APSR, callee restoration, SP and interrupt masks. Another 2,560 paired observer
invocations execute the actual disconnect-to-helper chain for all three links,
invalid handles and repeated events. Only the selected link changes; no provider
or supervisor call is permitted in this path. Five negative controls reject
wrong data length, uncleared pending state, wrong MTU, merged stores and reordered
stores. Their runtime checks deliberately disable the preliminary byte-equality
assertion so rejection tests the behavioral oracle.

The full R1 build compiles/composes 590 units without known failures or duplicate
strong symbols. Application imports decrease from 160 to 159; bootloader imports
remain 34. The other 589 objects, and the changed unit's prior allocated sections
and relocations, remain unchanged.

The admitted helper increases source-built bytes from 4,245 to 4,269 and reduces
binary-pull-through bytes to 641,891; resource bytes remain 248. The hybrid
application still equals the locked official artifact, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The full observer is not byte-identical. Link setup, MTU/data-length events,
radio/SoftDevice operations, arbitrary faults and concurrency are unproven.
Whole-observer caller-clobbered values, APSR and private stack spills are excluded
from the integration comparison. Complete source linking, physical hardware
support and a byte-identical source rebuild remain unfinished.

The [receipt](gatt-link-c-review.json) records exact inputs and results. Ignored
reproduction inputs are under `build/goal-r1-gatt-link-c/`; current reports are
`build/sources-goal-r1-gatt-link-c-final/report.json` and
`build/hybrid-goal-r1-gatt-link-c/build-report.json`.

The newer [typed SDK call review](radio-sdk-c-review.md) reruns these regressions
while replacing handwritten radio supervisor-call wrappers.
