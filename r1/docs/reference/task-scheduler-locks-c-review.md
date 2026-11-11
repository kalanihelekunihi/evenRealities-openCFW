# Task creation with actual scheduler and critical routines

The task-creation comparison now executes the selected C implementations of
`vTaskSuspendAll`, `xTaskResumeAll`, `vPortEnterCritical` and
`vPortExitCritical`, alongside the actual allocator, memory fill, constructors,
list/stack initialization and ready insertion. Their stock counterparts also
execute without patched function bodies. Source-side instruction checks forbid
executing mapped stock code. The ownership entries for these four routines and
`xTaskIncrementTick` now name their actual selected source providers rather than
removed experiment paths or the excluded baseline CMSIS port.

[Machine-readable evidence](task-scheduler-locks-c-review.json) binds the current
source objects, native REA instruction observations, probes, controls,
qualification and hybrid report by SHA-256. Firmware sources and the manifest
are unchanged; the existing complete normal report is reused after checking its
manifest, relevant source and object hashes.

The principal matrix passes 1,932 paired traces containing 2,508 paired
constructor operations (5,016 root executions). It retains mixed static/dynamic
tasks, names, depth/allocation boundaries, four xPSR word values and logical
fault checks, and adds three critical contexts: nesting zero with entry BASEPRI
zero or 64, and nesting two with BASEPRI 64. Port nesting/state words are now
part of the RAM comparison. Actual critical exit clears BASEPRI when nesting
reaches zero; it does not restore an arbitrary entry mask. Nested execution
retains BASEPRI 64. This replaces the earlier modeled-boundary assumption for
these integrated paths.

A further 144 paired traces contain 432 paired constructor operations and 324
paired calls of the actual tick-increment routine. Seeded pending ticks are
processed by actual scheduler resume code, including wrap from 0xffffffff,
delayed/overflow-list pointer exchange, overflow-count updates, equal-priority
time slicing and PendSV/SEV/DSB/ISB observations. Independent checks verify the
number of replayed ticks, resulting tick/pended counters and list pointers.
All-static or first-task-only dynamic allocation paths correctly leave the
pending count unprocessed until an eligible resume.

No function stubs are installed in these stock/C creation paths. Core registers
are mapped without asynchronous interrupt delivery, and PRIMASK holds off
exceptions. RAM placement is fixed only in the fixture. Allocation caller words
and task-exit LR words retain the earlier checked normalization; complete heap,
static task/stack guards and scheduler/list state compare. Stable names and
valid ordinary pointers are assumed. Pending-ready task drain, delayed-task
wakeups, physical context switches, MMIO timing, complete exception state,
private frame identity and caller-clobbered words/flags remain separate gates.
This is not full scheduler or hardware proof.

Controls that retain BASEPRI on final exit, omit scheduler suspension or skip
pending-tick replay are rejected. Fresh REA observations confirm the native
10-byte suspend, 276-byte resume, 40-byte critical-entry and 32-byte critical-exit
bodies. Fifteen qualification profiles across the three source providers select
no exact new regions. The canonical plan is unchanged at 3,857 source-built
bytes, 642,303 executable pull-through bytes and 248 resource bytes. A fresh
hybrid still equals the locked application byte for byte. The existing 573-unit
normal build has 179 application and 34 bootloader imports, with no failures or
duplicate strong symbols. Complete source linking, source completeness and
physical operation remain unfinished; no G2 gate advances.
