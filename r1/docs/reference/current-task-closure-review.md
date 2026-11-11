# R1 shared current-task cell and C getter

The selected task-count unit now owns one four-byte, volatile `pxCurrentTCB`
cell initialized to zero and the pinned FreeRTOS C implementation of
`xTaskGetCurrentTaskHandle`. Existing selected scheduler and port consumers
resolve to that single definition. The normal R1 composition has 227 unresolved
application imports, down from 229, and 34 bootloader imports. All 562 units
compile without failures or duplicate strong symbols.

Stock getter `0x9879c` reads the word at `0x2000781c` and returns it without
dereferencing the task object. REA/Ghidra confirms that read and return. The
word belongs to compressed RW initialization, not BSS: stock decoder `0x286f4`
expands the region from `0xc4610` to `0x200064a8` for 6,492 bytes. Independent
decoding and execution of the authenticated stock decoder produce identical
bytes, preserve surrounding guards, and establish a zero initial pointer.
The expanded region SHA-256 is
`87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317`.

The getter comparison passes 1,064 scenarios and 4,256 total stock/source
invocations, including repeated calls with changed pointer values, opaque and
unaligned values, and BASEPRI/PRIMASK combinations. Each call performs one
four-byte cell read, no writes, preserves callee-saved registers and stack,
and leaves interrupt masks unchanged. The four previously built query
function bodies remain unchanged. The candidate getter is 12 bytes versus
six stock bytes; this is behavioral evidence, not byte equality.

The C cell uses `.r1.rtos.current_tcb`, with four-byte alignment and explicit
zero contents. Probe addresses are normalized by storage role. The final
firmware linker must place the cell at `0x2000781c`; relocatable composition
does not establish that placement. Other compressed RW contents, complete
kernel initialization, full linking, physical execution and whole-image byte
identity remain open. No source-plan selection or G2 workflow gate changed.

Hashes, consumer ownership, report bindings and ignored probe paths are in
[the machine-readable review](current-task-closure-review.json). The build
report is `build/sources-goal-r1-current-task/report.json`; probe scripts and
REA evidence are under `build/goal-r1-current-task/`.
