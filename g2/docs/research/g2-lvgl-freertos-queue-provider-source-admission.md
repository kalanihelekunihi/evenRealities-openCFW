# G2 LVGL FreeRTOS queue-provider source admission

Status date: 2026-08-30  
Scope: the three FreeRTOS imports in the maximal LVGL/Ambiq/Nema link  
Mode: authenticated source reuse, bounded exact-ABI adapter, hostile host tests,
and Cortex-M55 relocatable-link verification; no production routing, scheduler
execution, flashing, or hardware operation

## Result

The remaining coherent FreeRTOS group is now closed by a component-local
provider for:

- `xQueueGenericCreate`;
- `xQueueGiveFromISR`; and
- `xQueueSemaphoreTake`.

The adapter exports the exact FreeRTOS public calling convention: 32-bit
`BaseType_t`, `UBaseType_t`, and `TickType_t`, an opaque Queue handle, and an
eight-bit queue-type argument. It forwards valid calls to already
source-qualified G2 implementations derived from authenticated
FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` under the MIT license.

The maximal missing-provider ledger falls from 73 to 70 symbols. Its digest is
`37340f0fbd8565aa40fbbdb282480ceb48fe7de68e7d27847931c048a8eb637d`.
No `xQueue*`, Nema HAL, or Apollo HAL import remains in that ledger. This is an
isolated source/link result, not production or scheduler-runtime admission.

## Exact Nema use

The authenticated Apollo510-EVB Nema HAL uses FreeRTOS macros whose emitted
imports are pinned by target relocations. Binary-semaphore creation reaches
`xQueueGenericCreate(1, 0, 3)`. The GPU interrupt gives that semaphore through
`xQueueGiveFromISR`, preserving the optional higher-priority-task-woken output.
Command-list and mutex wait paths reach `xQueueSemaphoreTake`, including the
full 32-bit tick range used by `portMAX_DELAY`.

The adapter does not substitute CMSIS wrapper semantics. It supplies the
underlying FreeRTOS APIs emitted by those macros.

## Bounded failure behavior

Normal inputs retain the authenticated FreeRTOS behavior. The adapter adds
three bounded checks before reaching stock-compatible assertion seams:

- zero-length dynamic queue creation returns null;
- multiplication or addition that cannot fit the 32-bit payload plus the
  authenticated `0x50`-byte G2 `Queue_t` returns null; and
- null queue handles passed to give or take return `pdFAIL`/`errQUEUE_EMPTY`
  value zero without touching the optional wake pointer.

The highest accepted payload is exactly `UINT32_MAX - 0x50`. Queue type values
remain eight-bit and are forwarded unchanged, as in the public generic API.
The adapter cannot safely classify arbitrary non-null addresses without owning
the allocator and G2 memory map, so such pointers retain the underlying
FreeRTOS contract rather than being guessed valid.

`tests.test_runtime_lvgl_ambiq_freertos_queue_provider` verifies normal binary
semaphore creation, zero length, multiplication wrap, addition wrap, the exact
upper payload boundary, null give/take, optional null wake output, full tick
range, exact queue pointers and arguments, optional wake-output semantics, and
return propagation. On the target, the public ARM_CM55 port's `long`-based
`BaseType_t` is compile-checked against the authenticated public prototypes;
the internal fixed-width implementation uses a local 32-bit wake-value bridge
to avoid incompatible-pointer aliasing.

## Target closure

The atomic auditor pins nine source/header inputs by path, size, SHA-256, and
MIT license. Five C inputs are compiled independently for `arm-none-eabi`,
Cortex-M55, Thumb, hard float, short enums, freestanding GNU C11, `-O2`,
section splitting, and warnings as errors.

The adapter contains exactly:

- two `R_ARM_THM_JUMP24` relocations to the dynamic-create implementation,
  covering zero-item-size and nonzero-item-size valid paths;
- one `R_ARM_THM_JUMP24` plus one `R_ARM_THM_CALL` relocation to give-from-ISR,
  covering null and non-null optional wake-output paths; and
- one `R_ARM_THM_JUMP24` relocation to semaphore-take.

`ld.lld -r --gc-sections` retains the three public exports plus six reachable
`open_cfw_*` implementation exports. The complete 6,404-byte object has
SHA-256
`926b0597a2d78ea441151b2c21cfc813be29bb246606b2a6b0c5d84e5b175608`
and no ELF undefined symbol. The source identities, complete nine-symbol
export set, adapter imports/relocations, object size, and object digest all
fail closed on drift.

With the exact scoped AmbiqSuite archives and EVB HAL, the maximal partial link
is 1,561,976 bytes with SHA-256
`9bda2df1b21fd0c0cb93ff9bf1c954c7af42a06aee3170584d061cbf57fa4ef0`.
It has the same 70-symbol residual and no Nema/Apollo/FreeRTOS queue import.

## Fixed G2 runtime boundary

Zero ELF imports do not make this provider a standalone scheduler. Its
reachable sources materialize 27 pinned G2 dependencies: queue reset and heap
allocation; assertion and ISR/task critical primitives; task count, scheduler
state, suspend/resume, timeout, event-list, yield, mutex-inheritance, and queue
helpers; plus current-TCB, ready-list, pending-ready, top-priority,
yield-pending, and scheduler-suspended RAM objects.

Every address is machine-recorded in
`tools/manifests/g2-lvgl-nema-link-admission.json`, and the final object digest
also pins its compiled representation. This work does not newly route or
execute those addresses. Scheduler concurrency, ISR priority, allocation,
timeout behavior, wake/yield behavior, and GPU command completion therefore
remain runtime-unqualified. No live hardware behavior is claimed.

## Reproduction

From `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_freertos_queue_provider
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
```

Production integration requires a deliberate review of the complete fixed G2
scheduler/RAM boundary and atomic routing with the Nema and Apollo providers.
