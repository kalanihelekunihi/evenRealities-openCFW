# uLED MSPI setup and handle publication

REA/Ghidra 12.1.4 inspected the locked Apollo main initialization function
at 0x59CF1A (572 bytes) and the type-0/type-1 setup functions at 0x592680
and 0x5BBD70 (52 bytes each). This extends the
[callback handle review](uled-irq-handle-review.md); it is not whole-image
or independently reviewed coverage.

## Instruction-backed behavior

Both setup functions reject a zero first argument with UINT32_MAX and no
state writes. Otherwise they first store that argument in their context
cell, then store the second argument in the neighboring argument cell:

| Panel | First write: context | Second write: argument | Published MSPI handle |
| --- | --- | --- | --- |
| Type 0 | 0x2007452C | 0x20074528 | 0x20074524 |
| Type 1 | 0x20074518 | 0x20074514 | 0x20074510 |

The new raw decompiler output reverses these independent stores in its
pseudocode. The native assembly and existing volatile C preserve the actual
order (0x592692 then 0x592698; 0x5BBD82 then 0x5BBD88). Thus pseudocode text
alone is insufficient evidence for ordered state effects.

The setup functions call 0x59CF1A with the address of the handle cell, the
third setup argument, and fixed serial/quad configuration pointers. They
ignore the initializer's return status, call the panel-enable function with
1, and return that function's result. This includes initialization failure
paths; the review does not replace stock behavior with speculative cleanup.
The existing C initializer declaration in the setup TU now correctly uses a
`uint32_t *` output parameter. The isolated linked binary was unchanged by
this type correction.

Initializer 0x59CF1A:

1. Publishes serial/quad configuration at 0x20074538/3C.
2. Creates the binary semaphore and stores it at 0x20074534; a NULL semaphore
   result is not checked in this body.
3. Initializes MSPI instance 0, wakes it, configures the command queue and
   device, enables it and selects pin mode 0.
4. Clears and enables interrupt mask 0x1A80.
5. Programs IRQ 20 priority 4 (byte 0x40 at 0xE000E414), then enables it
   (0x00100000 at 0xE000E100).
6. Requests deep sleep, ignoring that final power helper's return status.
7. Only then stores the handle through its output pointer and returns 0.

Failures before publication leave the caller's output word untouched. Most
failure branches log, while interrupt-clear failure returns UINT32_MAX
without that logging sequence. All of this agrees with the existing C.

The enable-before-publication order explains why the callback's NULL-cell
guard matters during initial startup. It does not prove global handle
validity: aliases, repeated initialization, other writers and HAL lifetime
rules still require whole-image reconciliation.

## Execution checks

All **221 stock/C cases passed** across the initializer and both setup
functions. Tests cover each lower-helper failure, all eight log-flag
combinations, a NULL semaphore result, a failed final sleep request, and
NULL setup context. They compare ordered shared-cell/NVIC writes, helper
arguments and call order, fixed logging fields, return status and output
publication. HAL/RTOS/panel/log helpers were controlled mocks; this does not
verify their implementations, peripheral timing or interrupt concurrency.

The analysis-only wrapper, snapshots and probes are under
`build/goal-uled-irq/`. Raw observations, identities, comparison cases and
limitations are retained in
[`uled-mspi-init-review.json`](../../evidence/uled-mspi-init-review.json).
No firmware oracle, source plan or workflow gate changed.
