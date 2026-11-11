# C task-selection boundary

The ownership entry for native `vTaskSwitchContext` (0x965ac, 128 bytes) now
names the selected `rtos/context-port/selection.c` provider instead of the removed
pre-consolidation experiment. The C algorithm is unchanged.

[The receipt](context-selection-c-review.json) binds the source, current object,
probe, negative controls and qualification. There are 2,168 paired stock/C cases
(4,336 executions), covering highest-priority search with stale top-priority
hints, one/two/three ready tasks, list-index/sentinel wrap, scheduler suspension,
entry masks, absent ready tasks and the four-word stack guard. Corruption of the
fifth word alone correctly does not trigger the four-word guard. Suspended
selection avoids current-task dereferences, including a null current pointer.
Full guarded task/stack/list/global snapshots compare. Independent assertions
check selected task, ready-list index, top priority, yield-pending state, final
SP, callee-saved registers and masks. A head-only selection mutation and omitted
stack guard are rejected.

Normal selection executes without function stubs. For corrupt stacks, the
probe records the overflow hook's task/name arguments and stops at hook entry;
it does not execute the terminal logger/drain loop. Empty-ready-list logical
assertion mask/address/width/value are checked without full exception state.
Private frame identity, caller-clobbered words/flags and physical scheduling
remain unverified. SVC/PendSV architectural register/frame save/restore is a
separate low-level boundary; these selector tests do not justify replacing it
with ordinary C.

Five qualification profiles select no exact new region. Firmware C, manifest
and canonical source-plan bytes are unchanged. The existing 573-unit source
report remains applicable, with 179 application and 34 bootloader imports and
no failures or duplicate strong symbols. This is bounded execution evidence,
not full source linking, byte qualification or hardware proof. No G2 gate advances.
