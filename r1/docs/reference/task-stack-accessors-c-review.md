# R1 native task stack diagnostic accessors in C

`vTaskStackAddr` and `vTaskStackSize` now have C implementations in the existing
`rtos/task-count/task-count.c` unit. These close two CmBacktrace dependencies
using the recovered 112-byte native TCB. The current task is read from the shared
`pxCurrentTCB` cell; stack base comes from offset 48, and the full 32-bit stack
entry count comes from offset 84. The count is not converted to bytes. No
null-current fallback is invented.

REA/Ghidra confirms the stock eight-byte bodies at `0x964b0` and `0x964bc`.
Their separate literal words both resolve to the current-task cell at
`0x2000781c`. The ELF analysis wrapper's text is the locked application;
provider instruction text is evidence of these local bodies, not corpus coverage.

The normal object passes 320 paired stock/C emulator cases. The qualified `-Oz`
object passes the same cases. Cases vary current task, stack pointer, 32-bit
stack depth and BASEPRI; they also check the null-current memory fault. Ordered
32-bit field reads, untouched TCB/current-cell guards, returned value, saved
registers, successful-return SP and interrupt masks agree. Mutating depth to
bytes or using the saved top-of-stack field is rejected. Existing functions in
the changed object retain their instruction-body bytes, and all other source
objects retain their hashes.

All 573 R1 units compile without failures or duplicate strong symbols. Application
imports fall from 179 to 177; bootloader imports remain 34. The manifest is
unchanged. This does not establish a final source-only link.

The official qualifier compiled five profiles and selected two `-Oz` regions:
each eight-byte C body plus its four-byte relocated pointer literal is exact.
The 24 bytes were checked for overlaps, merged into a staged source plan, and
verified in a complete stock-identical hybrid application before promotion to
`tools/build/source-plan.json`. A fresh build using the promoted plan also
matches the locked 646,408-byte application. Source-built bytes increase from
3,857 to 3,881; binary pull-through decreases to 642,279; resource bytes remain
248. These are total stored-byte provenance counts, not whole executable-C
coverage. Source completeness remains false.

This evidence covers synchronous seeded task state in an emulator. It excludes
asynchronous task switching, physical crashes, complete unwind behavior,
caller-clobbered registers/flags and private stack traffic. The diagnostic name
wrapper and the remaining hardware/RTOS imports remain separate work. The
existing stack-sensitive assembly bridges are retained pending stronger evidence
for a C replacement. No G2 implementation or workflow gate was changed.

Hashes, build paths, qualification details and limits are recorded in
[task-stack-accessors-c-review.json](task-stack-accessors-c-review.json).
