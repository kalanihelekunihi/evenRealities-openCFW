# R1 SpO2 stream and timer lifecycle in C

Follow-up: the [scheduler](spo2-scheduler-c-review.md) is now implemented in C;
its sample and timeout callbacks remain native. Dependency/build counts below
describe this lifecycle review's earlier snapshot.

`native_spo2_lifecycle.c` implements the group-1 callback `0x4ad40`, timer
release `0x4b2e4` and group-4 wear callback `0x4b2fc` in ordinary C. The
[receipt](spo2-lifecycle-c-review.json) binds REA bytes, production hashes,
replay, startup initialization, rejected defects, qualification and builds.
The callbacks' previously unknown frontier extents are now **44 and 50 bytes**;
the timer helper is 20 bytes. The recovered helper name
`r1_stress_stream_release` is retained, although its callers unregister `spo2`.

The group-1 callback ignores its incoming argument. It reads timing-stream
slot 1, unregisters a nonzero handle, clears the slot **after** the provider,
then releases the freshly read timer and clears that timer late. It clears
flag bytes 1 and 2 separately, reloads mode after cleanup, and tail-calls the
remaining native scheduler `0x4af10` with argument **1** only for mode exactly
1. The scheduler's stock entry SP is preserved.

The wear callback captures its event byte before cleanup and returns only for
status exactly 1. Other statuses read both stream slots in sequence, unregister
nonzero handles with topic `spo2`, clear each late, then release the fresh timer.
It does not clear the timing flags or invoke the scheduler. The timer helper
also reads fresh and clears after release. Providers can change future handles,
mode, flags or timer during these calls; stock read/store ordering is preserved.

The unit owns **eight RW bytes at `0x20006d98`** and **eight ZI stream-handle
bytes at `0x2001a3d0`**. Stock scatter-handler execution on poisoned SRAM,
guard checks and an independent RW decoder establish cold mode **2**, with
all other owned bytes zero. No assembly is added. Adjacent storage is unowned.

Validation passed **4,608 paired cases: 4,544 completed calls and 64 expected
invalid-event faults**. Cases cover all handle masks, zero/nonzero timer,
modes/statuses 0/1/2/255, ignored invalid group-1 arguments, event aliases,
provider errors and mutations to current/future handles, timer, mode and flags.
Comparisons include provider order/arguments, public SRAM, write widths, saved
integer/FP registers, SP, masks and FPSCR. Faults precede providers and state
writes. Void R0, caller-clobbered registers/APSR and private stack bytes are
excluded. Lower unregister/timer-release and the remaining scheduler are
modeled; this does not establish full scheduling or physical operation.

Nine compiled defects were rejected: wrong stream slot, broad wear guard,
early timer/stream clears, whole-word flag clear, cached mode, wrong scheduler
argument, wrong topic and broad mode guard.

All **661 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **660 prior objects** are unchanged; the
registration source only adopts the recovered group-4 prototype. Resolving
both callbacks exposes `r1_spo2_timing_start_plan`, leaving **165 application /
34 bootloader imports**. None of the three bodies qualifies as instruction-exact.
The canonical plan stays at 4,369 source-built bytes, and the fresh hybrid
matches the locked application through executable pull-through. Complete
source-only linking, concurrent behavior and physical SpO2 stream/timer
operation remain unproven.

The subsequent [SpO2 control review](spo2-control-c-review.md) extends the canonical handle owner to three words for stock initial mode 2, authenticates all 20 state/handle bytes and preserves the existing lifecycle code and relocations.
