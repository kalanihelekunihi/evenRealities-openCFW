# Native task ready-list handoff validation

The ownership entry for stock 0x84d68 now names the current
`rtos/task-construction/ready.c` provider and its exported
`r1_native_task_add_ready` alias. It previously pointed only to a removed
pre-consolidation experiment, so the official qualifier could not select this
current source unit. The native identity and coverage count are unchanged.
Firmware C and manifest files are unchanged in this step.

[Machine-readable evidence](task-ready-handoff-c-review.json) binds the source,
REA instruction observation, probes, negative controls, qualification and hybrid
reports by SHA-256. REA confirms the 224-byte stock entry, list initialization,
current-task selection, counter/trace-number updates, ready insertion and
PendSV/SEV/DSB/ISB path. The selected C function is 358 bytes in its normal
profile; behavioral agreement is separate from instruction identity.

There are 3,456 paired standalone stock/C cases (6,912 executions). The actual
ready-list and list-initialization bodies execute. Cases cover first task,
existing/null current task, task/counter wrap boundaries, scheduler stopped/
running, priority relations, ready-list indices, interrupt masks, and injected
scheduler-cell mutation at critical exit. Complete guarded task/list/global
snapshots, critical observations, PendSV writes and barrier sequence agree.
Independent assertions check count/trace-number updates, priority-list linkage,
first-task delayed-list pointers, current-task choice and yield decision.
Controls for the equal-priority comparison, missing first-list initialization
and missing yield are rejected.

A further 350 paired stock/C cases (700 executions) run dynamic/static
constructors, actual task initialization, stack-frame/list-item code and the
actual ready-list handoff together. They cover names, depths, priority and
static-buffer assertion boundaries, optional output pointers and modeled
allocation failures. The earlier constructor receipt intercepted the ready
handoff; this extends that proof through its implementation. Only the task-exit
LR word is normalized after checking its source-specific function address.

Critical boundaries, memory fills and allocator/free operations remain modeled.
Native RAM placement is fixed only in the fixtures. Seeded accessed state and
synchronous mutation do not establish complete scheduler invariants,
asynchronous context switching or physical execution. Names are stable; malformed
pointers/depths, full exception state, private frame identity and caller-clobbered
words/flags remain outside the comparison. Actual allocator integration remains
a separate next dependency.

Five qualification profiles now compile this current provider but select no
exact regions. The canonical source plan remains unchanged: 3,857 source-built
bytes, 642,303 executable pull-through bytes and 248 resource bytes. A fresh
hybrid build still equals the locked application byte for byte. The existing
573-unit normal report remains applicable because its manifest and source are
unchanged: 179 application imports and 34 bootloader imports, no failures or
duplicate strong symbols. Complete source linking, source completeness and
hardware operation remain unfinished. No G2 corpus gate advances.
