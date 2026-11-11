# R1 watchdog-aware task name diagnostic in C

`vTaskName` now has a C implementation in the existing
`rtos/task-count/task-count.c` unit. It calls the selected
`r1_native_watchdog_expired_task` implementation, uses a nonzero returned task
handle, or then reads the shared current-task pointer. It returns the native
name address at task +52 without reading the name or dereferencing the task.
The existing native TCB declaration checks that offset. Pointer arithmetic uses
32-bit `uintptr_t`, including the stock null-current result `0x34` and wraparound;
no fallback string or handle validation is invented. This is the R1 diagnostic
wrapper, not a substitute for the distinct unresolved `pcTaskGetName` API.

REA/Ghidra confirms that the stock diagnostic has three disjoint body ranges:
`0x6a098..0x6a0af` calls the watchdog getter and chooses a name leaf,
`0x9615a..0x9615d` adds 52 to the supplied task, and
`0x9617c..0x96183` loads current task then adds 52. Its 36-byte inventory size
is their combined size, not a contiguous span starting at `0x6a098`.
The watchdog getter at `0x5da30` reads the fault-record pointer at `0x20006734`,
tests bit zero in the flags byte at record +16, and conditionally reads its task
handle at +4. The source getter already implements that behavior and is unchanged.

The actual source diagnostic and watchdog getter pass 1,600 paired stock/C
emulator cases without function stubs or C-side execution of stock code.
Cases vary the record pointer, high and low flags, task/current handles including
null and wrapping values, and BASEPRI. A getter-entry mutation of current task
checks that fallback is sampled after the getter; it does not assert physical
interrupt timing. Ordered shared reads, unchanged records and guards, result,
return SP, saved registers and interrupt masks agree. Two negative controls
(prefer current task and prefetch fallback before the getter) are rejected.
The old seven function bodies retain their bytes; all other source objects retain
their hashes.

All 573 R1 units compile with no failures or duplicate strong symbols. Application
imports decrease from 177 to 176, with no additions; bootloader imports remain 34.
The manifest is unchanged. Five official qualification profiles compile, but none
qualifies the new name wrapper. The two existing stack accessors still qualify;
they are already in the source plan and were not added again. The source plan is
unchanged. A fresh hybrid build still equals the complete locked 646,408-byte
application: 3,881 source-built bytes, 642,279 binary pull-through bytes and 248
resource bytes. These are stored-byte provenance counts, not executable-C
coverage. Full source completeness remains false.

The evidence covers seeded synchronous execution, not a physical watchdog expiry,
complete crash unwinding, asynchronous scheduling, private stack traffic or
caller-clobbered registers/flags. No G2 implementation or workflow gate changed.
The name wrapper has semantic evidence but no byte-identity qualification.
See [task-name-c-review.json](task-name-c-review.json) for hashes and build paths.
