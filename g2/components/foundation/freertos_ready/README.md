# Ordered waiter to ready/pending transition

This source-defined provider replaces the queue event-list-removal and task-count fixtures in the linked radio → WSF → EventGroup → timer-command queue simulator. It is a bounded FreeRTOS V10.5.1 subset, not a complete scheduler or firmware replacement.

`tasks_subset.c` and `list_subset.c` retain five unchanged MIT-licensed function texts from commit `def7d2df2b0506d3d249334974f51e427c17a41c`. `ready_compat.h` supplies authenticated private offsets/global cells and macros. The upstream remove function is renamed through preprocessing; `ready_adapter.c` preserves the earlier queue ABI. This is faithful stock behavior with no checked adapter or lifecycle protection.

Call removal with a nonempty ordered event list, initialized owning TCB/state lists and BASEPRI 0x30 held by the queue caller. Unsuspended removal transfers the state item to the priority ready list. Suspended removal transfers only the event item to pending-ready; the state item remains blocked. Both branches can return higher-priority=true and set yield-pending. That result does not prove the task has run or even entered a ready list.

Insertion occurs immediately before `pxIndex`, preserving the index; it is not unconditional append after the physical tail. Removal repairs an index pointing at the removed item. The next-unblock cell becomes the current delayed-list head tick, or 0xffffffff when empty. Units are ticks. The 48-byte TCB declaration covers only accessed fields; the synthetic 112-byte allocations are not a recovered complete TCB layout.

Build: `make -C g2 rtos-ready-wsf-simulator`. Run the verifier with the installed OpenCFW Python, ELF path and a fresh output filename. Native Unicorn may require sandbox approval. See `g2/analysis/rtos-ready-wsf-2026-10-05/REPORT.md` for comparison evidence and emulator policy.

Pending-ready drain, actual suspend/resume, task selection/context switch, allocation/deletion, and borrowed EventGroup lifetime remain outside this provider. No firmware patch, device execution or byte-identical build claim follows.
