# R1 stream timer rearm in C

`native_stream_timer_rearm.c` supplies stock `0x8a59e` as ordinary C with a
compiler BASEPRI intrinsic for the null-input fault path. The
[review receipt](timer-rearm-c-review.json) binds REA stock bytes, production
source/object hashes, differential fixtures, qualification and the locked hybrid.

For a nonzero timer it calls the existing tick provider, stores that returned
word at the original timer address plus four with 32-bit address wrapping, and
returns the existing wake provider's raw R0. Wake observes the timestamp store.
It does not clear the timer's stopped bit or return the timer pointer. A zero
timer sets BASEPRI to 64 and attempts the stock zero-word write at `0xffffffff`,
then loops if that write returns. No new RAM ownership or native imports are added.

There are 1,008 paired stock/C comparisons executing the actual C tick and wake
providers. Dynamic tick/wake callbacks and the OS fallback are modeled. Cases cover
unaligned timers, timestamp/result boundaries, timer aliases into housekeeping
and tick-getter cells, callback-time mutations, address wrapping, null faults and
interrupt masks. Another 864 paired cases execute the actual C raw-HR lifecycle,
rearm, tick and wake together, modeling the remaining stream/timer/OS providers.
Public state, write widths, arguments, R0 and logical faults are compared;
preserved registers and SP are checked on normal returns, with masks and FPSCR
also checked. Both native and C direct paths have eight-byte tick-provider frames
and restore the frame before wake callbacks. Fault PC, private stack residue,
caller-clobbered registers and APSR are excluded. Six compiled defects are rejected:
wrong fault mask, wrong field offset, lost timestamp, missing wake, wrong return
word and early wake. Physical/concurrent behavior remains unverified.

All 641 units compile and both relocatable compositions pass without duplicate
strong symbols. All 640 previous objects remain unchanged. The timer-rearm import
is resolved with no new imports, leaving application/bootloader imports at 174/34.
Manifest validation passes. Exact qualification rejects this body; the source plan
remains unchanged at 4,341 source-built bytes. A fresh hybrid matches the locked
application with 641,819 executable pull-through and 248 resource bytes. Complete
source-only linking and byte identity from C remain unfinished.
