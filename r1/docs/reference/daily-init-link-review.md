# R1 daily cache initialization linked into the source composition

`native_daily_metadata.c` now participates in the normal source composition.
It supplies six cache-initialization entries, their refresh bodies and local
day-start calculation in ordinary C. The [review receipt](daily-init-link-review.json)
binds production source/object hashes, REA bytes, replay artifacts, qualification,
RAM field checks and the promoted exact source plan.

The unit was previously excluded for duplicate definitions, leaving six task
initializers and `r1_time_local_day_start` unresolved. It now uses the existing
canonical `r1_time_utc_offset_get` instead of defining another copy. Five UTC-offset
fields already fall inside linked HR/HRV/SpO2/stress/temperature sample prefixes;
the refresh routines now write those canonical packed halfwords instead of owning
duplicate cells. Six timestamp words lie beyond the bounded prefixes, and the
activity offset remains a separate halfword: 26 newly linked owned bytes total.
Their stock addresses lie in the authenticated startup ZI range. Existing prefix
providers remain unchanged. This does not establish final source-only RAM placement.

Day start captures the signed UTC offset before obtaining the unsigned backend
timestamp, adds offset seconds in signed 64 bits, divides by 86,400 toward zero,
then subtracts the captured offset with 32-bit wrap. It deliberately does not use
floor division for negative adjusted times. Activity/HR/HRV/SpO2/temperature refresh
store that day start; stress stores the current backend timestamp. Each refresh
then obtains a fresh UTC offset and writes its low halfword. HR logging preserves
fresh mode/timestamp reads and raw return behavior. Six initializer entries forward
to these routines without introducing policy or state.

The fixture passes 1,156 paired native/C cases across all thirteen entries. It
executes the actual linked C UTC getter and signed-division runtime, with timestamp
and logging providers modeled. Cases cover signed halfword offset extremes,
unsigned epoch boundaries, negative adjusted time, backend mutation of the offset,
logging mutation of the timestamp, changing log modes and interrupt masks. Direct
day-start results also match an independent integer oracle. R0, memory and provider
traces are compared; callee-saved integer/FP registers, SP, masks and FPSCR are
checked. Caller-clobbered registers, APSR and private stack residue are excluded.
Six compiled defects are rejected: unsigned day division, wrong HRV offset,
stress using day start, wrong offset scale, lost offset stores and extra log queries.
Physical and concurrent behavior remain unverified.

All 633 units compile and both relocatable compositions pass without duplicate
strong symbols. All 632 other objects remain identical. Enabling this unit resolves
seven application imports, reducing 172 to 165; bootloader imports remain 34.
Only the stale exclusion/note is removed from its existing manifest entry. There
is exactly one participating UTC-offset getter. Manifest checks pass.

The six four-byte initializer branches pass exact qualification with native
refresh bindings. Their production and qualification instruction sections agree.
Only those 24 bytes enter the exact plan; the seven refresh/day-start bodies remain
behavior candidates. All previous plan units/regions remain intact. The preview
hybrid matches the locked artifact before canonical promotion. Current exclusive
provenance is 4,337 source-built, 641,823 executable pull-through and 248 resource
bytes. Complete source-only linking and firmware hardware validation remain
unfinished.
