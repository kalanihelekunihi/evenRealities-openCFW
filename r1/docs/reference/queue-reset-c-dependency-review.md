# Native queue-reset dependency in C

The selected queue/mutex provider now includes `xQueueGenericReset` from the
pinned FreeRTOS 10.5.1 source. It shares the existing 80-byte native Queue_t
layout, critical-section/assert configuration and list implementation. This
resolves an actual runtime import without enabling the duplicate full upstream
queue unit. All eleven preexisting function bodies in the selected object,
including its six exported queue/mutex functions, remain byte-unchanged.

Stock entry `0x97ba4` validates the queue, nonzero capacity and capacity/item-size
multiplication before entering the critical section. It clears the count,
resets data pointers and unlocks both counters. An existing queue wakes one
waiting sender when present, while a new queue initializes both event lists.
A wake request sets PendSV, executes SEV/DSB/ISB and then exits the critical
section. Native assertions mask BASEPRI to 64 and attempt a zero-word write at
`0xffffffff`; the selected configuration retains that logical fault behavior.

All 6,944 paired native/C cases pass (13,888 executions). They cover capacities,
item sizes, new/existing flags, sender counts, raw wake results, four starting
interrupt masks, critical-entry mutations of descriptor fields, scheduler
mutations retained after wake, null queues, zero lengths and overflow rejection.
Actual native/C list initialization executes. Queue bytes and boundary snapshots,
call order, preserved registers, SP, interrupt masks and PendSV/SEV/DSB/ISB order
agree. Negative controls reject skipping the yield, taking the wrong new-queue
list path and omitting count clearing.

REA/Ghidra decompilation failed with an address-range construction error, even
with an explicit Thumb entry/extent. Its instruction-only view successfully
returned the complete 168-byte function. Those instructions, direct disassembly,
the locked raw bytes and execution comparisons provide the stock evidence;
no successful pseudocode result is claimed.

All 573 R1 units compile and compose without failures or duplicate strong
symbols. Application imports drop from 197 to 196, with only
`xQueueGenericReset` removed and no new imports; bootloader imports remain 34.
`make sources-check` and `git diff --check` pass. Five official qualifier
configurations compiled; only two already-covered BASEPRI helper copies matched.
The new reset body is 166 bytes and remains unqualified.

The unchanged canonical plan still builds a stock-identical hybrid application,
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 3,833 source-built and 642,327 unclassified binary-pull-through bytes.
Source completeness remains false.

Critical entry/exit and event-list removal are modeled. Internal ordinary-memory
access order and private frames are excluded; callback stack depth is -24 native
versus -16 C. Assertion checks cover mask, fault address, width and value, without
claiming full processor exception state. Physical scheduling, concurrency,
interrupt delivery and sleep/wake remain unverified. No G2 gate advances. Exact
source, REA, probe, qualifier and build hashes are bound in the companion JSON.
