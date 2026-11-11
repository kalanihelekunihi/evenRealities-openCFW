# Compiled ring and battery calibration restore in C

The C implementation of stock `0x7c52c` closes event import
`r1_event_service_0007c52c`. It queries the controller address through the pinned
S140 gateway, formats the address in stock order and searches the compiled
calibration table. A match updates the existing ring-size and battery cached
classes and invokes the existing NV completion/check boundary.

The 826 table bytes are non-executable calibration data: 59 fourteen-byte rows
with 56 distinct addresses. The first matching row wins, including three pairs
of duplicate addresses. The low nibble selects ring size, the high nibble selects
battery type, and the signed calibration byte becomes a little-endian int16.
The existing reserved battery byte survives successful reads. No persistent
state or duplicate KV owner is added.

All 2,829 stock/C comparisons pass and cover every one of the 494 native
instruction bytes. Cases include every table-row input, logging modes, SVC
errors, nonmatches, reserved bytes, live handle replacement and ignored KV
statuses. The SVC gateway and actual C comparison execute; formatting, KV and
logging are modeled in this direct replay.

Another 724 cases execute the actual C battery getter, cached-class reads and
writes, memory routines and comparison. They check payloads, dirty flags,
reserved-byte preservation and balanced critical sections. Nine C-only cases
check a defined zero reserved byte after a non-writing failed cached read.
Four compiled defects changing ADC signedness, ring nibble, reserved-byte
preservation and first-duplicate selection are rejected.

The normal open-source build compiles 853 units and composes both payloads.
All 842 prior nongenerated objects remain unchanged. Application imports fall
from 66 to 65; bootloader imports remain 22. R1 manifest validation passes.

Physical calibration, radio operation, persistent flash writes, final linking
and boot remain unverified. The stock table is authenticated against the locked
artifact and REA, but this review makes no byte-identical firmware claim.
[Machine evidence](nv-default-restore-c-review.json) binds sources, table, REA,
replays, negative controls and build reports.
