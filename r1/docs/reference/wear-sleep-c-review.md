# R1 wear sleep-status callback in C

`native_wear_sleep_status.c` supplies stock `0x3d1b8` as ordinary C. The
[review receipt](wear-sleep-c-review.json) binds REA stock bytes, production
source/object hashes, differential checks, native initialization and qualification.

The callback captures one payload byte. If that byte is 1 and the previous sleep
status is zero, it clears the separate latch; it then publishes the captured byte.
Log modes retain fresh queries and stock short-circuit ordering. Each enabled
log path freshly reads the status, allowing provider mutations to affect the
reported value. The callback accepts all byte values rather than normalizing to
a boolean, and preserves a null-payload read fault. The startup module's declaration
now uses the established pointer argument; its compiled object is unchanged.

Only status `0x20006e95` and latch `0x20006e96` are newly owned. Native RW/ZI
handlers run on poisoned memory with guards, and an independent RW decoder
confirms both bytes start at zero. Surrounding wear control remains separate;
final source-only placement remains unproven.

The fixture passes 3,458 paired stock/C cases covering zero/one/other status
bytes, previous status and latch boundaries, changing modes, provider mutations,
input aliases into status/latch/adjacent control, null faults and interrupt masks.
It compares public memory, write widths, provider arguments and logical faults,
and checks preserved registers/SP on normal returns plus masks and FPSCR. Six
compiled defects are rejected: wrong transition condition, lost latch clear,
stale logged value, wrong structured tag, wrong SDK tag and premature status
publication. Log and mode providers remain modeled. Void R0, fault PC,
caller-clobbered registers, APSR and private stack residue are excluded.
Physical/concurrent behavior remains unverified.

All 642 units compile and both relocatable compositions pass without duplicate
strong symbols. All 641 previous objects remain unchanged, including the module
whose prototype was refined. The callback import is resolved without new imports,
leaving application/bootloader imports at 173/34. Manifest validation passes.
The working inventory now records its 86-byte executable span. Exact qualification
rejects this body, so the plan remains at 4,341 source-built bytes. A fresh hybrid
matches the locked application with 641,819 executable pull-through and 248 resource
bytes. Complete source-only linking and byte identity from C remain unfinished.
