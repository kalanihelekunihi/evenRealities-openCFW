# R1 cached local-time provider linked into the source composition

`native_log_calendar.c` now participates in the normal source composition,
resolving `r1_log_local_datetime_fill` at `0x8ac28`. Its cache management,
arithmetic and ordered copies are C, with an explicit raw-frame bridge. The
[review receipt](log-calendar-link-review.json) binds source/object hashes, REA
bytes, replay artifacts, negative controls, qualification and normal composition.

The provider returns immediately for a null output or unregistered clock. It
obtains the timestamp before reading the signed UTC offset, computes local day
start with signed 64-bit division toward zero, and refreshes date fields only
when the cache is invalid or its day differs. The converter receives a wrapping
32-bit local epoch. A null converter result leaves date-cache fields unchanged.
Otherwise, narrow sequential loads/stores preserve returned-buffer aliases:
year uses a halfword, then month/day/weekday bytes are read and stored before day
start and valid state are installed. Time fields use the captured original
timestamp/offset even if conversion mutates the state. The two final output words
are loaded/stored sequentially, preserving output aliases into the cache. The raw
native return is the unsigned seconds remainder, rather than a normalized status.

The old excluded C body did not preserve the converter's scratch-frame contract
or sequential packed-copy behavior. The revised bridge retains the 104-byte native
frame: epoch at caller SP-88 and 36-byte converter scratch at SP-76. Partial writes
and alternate returned pointers do not cause zero initialization of raw scratch.
The C worker adds provider-call depth: 136 bytes versus native 104. Exposed pointers
and scratch bytes are compared, while private worker stack and caller-clobbered
registers/APSR are excluded. Callee-saved integer/FP registers, SP, masks and FPSCR
are checked. No new RAM globals are introduced.

The fixture passes 2,160 paired native/C cases. Of these, 1,800 use the actual C
calendar converter and signed-division runtime; 360 model partial, null, external
and state-aliased converter returns. Cases cover clock registration/cache gates,
extreme signed offsets and unsigned epochs, timestamp-callback offset mutations,
registration changes after entry, preserved raw scratch and unaligned/aliased
outputs. Six compiled defects are rejected: early offset read, zeroed scratch,
lost valid flag, wrong output word, unsigned remainder and lost raw return.
Timestamp acquisition remains modeled. Physical and concurrent behavior remain
unverified.

All 633 units compile and both relocatable compositions pass without duplicate
strong symbols. All 632 other objects remain identical. The manifest removes only
this unit's exclusion. Application imports fall from 165 to 164; bootloader imports
remain 34. Manifest checks pass. This root does not pass byte qualification, so
the exact plan remains unchanged at 4,337 source-built bytes. A fresh hybrid
application matches the locked artifact, retaining 641,823 executable pull-through
bytes and 248 resource bytes. Complete source-only linking, final source-only RAM
placement and firmware hardware validation remain unfinished.
