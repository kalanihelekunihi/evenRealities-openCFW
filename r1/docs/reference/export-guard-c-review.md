# R1 EP export guard and poll/force entries in C

`native_export_guard.c` implements stock guard `0x3ed34`, poll entry `0x5e0de` and force entry `0x5e0e4`. The existing persistence-then-poll event adapter at `0x42bb0` also executes in the probe; its assembly body is unchanged.

For an unforced call with export paused, the guard reads the RTOS tick before reloading the saved pause timestamp, uses unsigned subtraction and returns while elapsed time is below 307,200 ticks. Timeout logging precedes clearing the pause byte. A forced call bypasses the pause check and does not itself clear the pause byte. If inactive, it invokes plan initialization and reloads active state. It then requires a nonzero semaphore handle and exactly 1 from a take with timeout 1,024. Successful acquisition runs the ring flush and reloads the semaphore handle afterward for a generic-send release with three zero arguments.

Four narrow RW owners cover active byte `0x2000693a`, paused byte `0x2000693b`, mutex handle `0x20006940` and pause timestamp `0x20006944`. They exclude the existing status-ring read/write/drop owners and all intervening bytes. Stock startup execution, independent RW decoding and compiled-object comparison confirm zero initial contents. See [startup proof](export-guard-initialization.json).

The guard, poll/force entry points and actual event adapter pass 1,668 stock/C comparisons. Cases cover noncanonical boolean values, timeout equality and wraparound, individual/changing log flags, failed initialization, missing handles, take results 0/1/2/`0xffffffff`, provider mutations and mixed poll/force sequences. Provider order/arguments, guarded shared state, preserved registers, stack pointer and interrupt masks match. Reconstructed execution is forbidden from entering stock instruction addresses. Private scratch, caller-clobbered registers and void returns are excluded.

Eight compiled defects are rejected: lost force bypass, wrong timeout boundary, signed elapsed comparison, early pause clearing, lost active-state recheck, broad semaphore-success gate, cached release handle and release-before-flush ordering. The full normal implementation was rerun afterward.

REA returned the complete guard and both six-byte entry points, verified against the official raw application. See [guard evidence](export-guard-c-rea.json), [entry evidence](export-guard-entries-c-rea.json) and [structured verification](export-guard-c-review.json).

All 766 R1 units compile and both payloads compose without duplicate strong symbols. All 765 prior objects are identical. Application imports change from 126 to 127: the poll event service closes, while `r1_ep_plan_initialization` and `r1_ep_export_ring_flush` become explicit. Bootloader imports remain 34. R1 source coverage passes. Global coverage retains the existing G2 `resident_rom_thumb_set.S` manifest omission.

Plan initialization, ring flushing, queue/semaphore operations, clock, persistence and logging are modeled boundaries. Real queue contention, flash export, asynchronous scheduling, complete firmware linking and physical device behavior remain unverified. Byte identity is not required for this build route.

# Snapshot start and finish callbacks, 2026-11-11

The stock descriptor callbacks at `0x58d64` and `0x58d54` now have
source-owned C bodies in `native_export_guard.c` as
`r1_log_export_snapshot_start` and `r1_log_export_snapshot_finish`.
Start logs before raising the existing structured-log export byte at
`0x20006906`, then snapshots `xTaskGetTickCount` and raises the existing
EP pause byte at `0x2000693b`. Finish clears both bytes and publishes the
zero-length `0x2003` event, returning that publisher's result.

The ignored host probe at `build/r1-export-guards-c-20261111/` executes
the C bodies for 2,048 log-mode/tick combinations under ASan and UBSan.
The stock ARM probe in the same directory executes `0x58d64` and
`0x58d54` from the locked 2.2.6.0009 binary with external providers
mocked and confirms the byte, timestamp, return and event state.

`build/sources-r1-export-guards-c-20261111/report.json` compiles all
939 application and 82 bootloader units without failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-export-guards-c-20261111/report.json` retains 12 unresolved
functions and uses 644,640 of 696,320 flash bytes. The strict bootloader
receipt at `build/r1-boot-link-export-guards-c-20261111/report.json`
links with a valid vector. The later
[export command](export-command-c-review.md) connects these callbacks to
the source-owned virtual-file path; live device behavior is still unverified.
