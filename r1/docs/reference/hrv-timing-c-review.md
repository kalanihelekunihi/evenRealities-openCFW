# R1 HRV timing cleanup and restart coordination in C

Follow-up: the [scheduler](hrv-scheduler-c-review.md) is now implemented in C;
its timeout and producer callbacks remain dependencies. Counts and dependency
status below describe the cleanup review's earlier build.

`native_hrv_timing.c` supplies session teardown `0x49e00` (30 bytes), the
group-1 callback `0x49e2c` (38 bytes), and timer release `0x49ef4` (20 bytes)
in ordinary C. The [receipt](hrv-timing-c-review.json) binds production source
and object hashes, REA bytes, replay, startup initialization and qualification.

The callback tests the timer field once. If nonzero, it tears down the session
and then releases the freshly read timer. It clears flag bytes 1 and 2 even
when there was no timer, reloads the mode byte after cleanup, and invokes the
remaining native scheduler with argument **1** only when the mode equals 1.
Its incoming event and return value are unused by the multicast boundary.
REA's function dossier merges the tail-called scheduler into the callback's
pseudocode; decoded instructions establish the separate 38-byte callback body.
The scheduler `0x49f0c` remains a dependency, rather than being treated as
implemented through that merged pseudocode.

Session teardown captures a stream handle and unregisters `"hrv"` when nonzero,
then clears the stream field **after** that provider returns. It always clears
the 208-byte session buffer, including when there was no stream. Timer release
also clears its field after the provider returns. Provider mutations are
therefore visible before the late clears; newly written handles can be lost,
as in stock. The recovered name `r1_hrv_stream_release` is retained even though
the released object is a timer.

The unit owns the 20-byte state at `0x20006d84` and 208-byte session buffer at
`0x2001a300`. Executing both stock scatter handlers on poisoned SRAM, with
region guards and an independent compressed RW decoder, establishes the exact
cold image: state mode **4**, all other bytes zero. This does not establish
whole-firmware RAM placement in a final source-only link.

Validation completed 7,680 direct paired stock/C cases and 4,608 further cases
executing the actual C EABI memory-clear wrapper and musl memset. Callback
tests also execute the new C teardown and timer-release routines. Cases cover
zero/nonzero handles, modes 0/1/4/255, ignored null/invalid event arguments,
provider failures, and provider changes to mode, flags, stream and timer.
Calls, arguments, public SRAM and guards agree; SP, saved integer/FP registers,
interrupt masks and FPSCR are preserved. Void R0, caller-clobbered registers,
APSR and private stack bytes are excluded. Unregister, lower timer release
and the remaining scheduler are modeled providers. Seven compiled defects
were rejected: early stream/timer clears, wrong topic, short buffer clear,
wrong restart argument, cached mode, and omitted flag clear.

The normal build compiles 653 units with both relocatable compositions passing
and no duplicate strong symbols. All 652 previous source/object hashes remain
unchanged. Resolving the callback exposes `r1_hrv_timing_start_plan`, leaving
169 application and 34 bootloader imports. None of the three bodies qualifies
as instruction-exact under the production bindings. The canonical plan stays
unchanged at 4,369 source-built bytes; the fresh hybrid application still
matches the locked artifact through executable pull-through. Complete C-only
linking, full scheduling, concurrent behavior and physical hardware operation
remain unproven.
