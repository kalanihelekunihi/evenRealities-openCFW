# G2 LVGL/Ambiq mutex provider source admission

Status date: 2026-08-30  
Scope: the notify-mode-independent mutex subset of the LVGL FreeRTOS OSAL  
Mode: authenticated source/layout evidence, hostile host gates, exact
Cortex-M55 ABI/relocation audit; no production routing, firmware integration,
flashing, or hardware operation

## Result

An isolated component-local provider closes `lv_mutex_init`, `lv_mutex_lock`,
`lv_mutex_unlock`, and `lv_mutex_delete`. These are the largest cohesive
remaining LVGL OSAL subset whose source and layout do not depend on the
unrecovered `LV_USE_FREERTOS_TASK_NOTIFY` selection. The maximal residual
moves from 35 to 31 symbols with canonical digest
`3d9a8dfcb9925ca8eebe8eafd1bf57d26752d7be6bb30830351dae2851116295`.

The 2,168-byte provider has SHA-256
`5067d94d102f8f6ce7090534a482657761ddee527f796db2cb330bedb36baf3a`.
It exports exactly the four mutex APIs, has no undefined ELF symbol or
external relocation, and closes the four retained Ambiq backend call sites.
The exact scoped AmbiqSuite/Apollo510-EVB maximal partial is 1,583,656 bytes,
SHA-256
`02f98e3b255eda4fec6e504efb83ea993a7996f276ba9741847deb071adf64e1`,
and independently reproduces the 31-symbol residual.

This is an isolated source/link result. The provider is not registered in the
Apollo production overlay.

## Source and ABI boundary

The semantic baseline is the exact `lv_freertos.c`, `lv_freertos.h`, and
`lv_os.h` Git blobs at the authenticated LVGL compatibility commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`. The manifest pins blob SHA-1,
byte count, and SHA-256 for all three. The target ABI is an eight-byte
`lv_mutex_t`: four-byte `BaseType_t xIsInitialized` at offset zero followed by
the four-byte recursive-mutex handle at offset four. `lv_result_t` is the G2
one-byte short enum with invalid `0` and success `1`.

The 2,056-byte ABI probe has SHA-256
`2067a9388bfeac43fe5ac2594c8bbdd35047b913cf3c5cb28ff442f319736d64`.
It includes the authenticated LVGL public OSAL header, asserts every width and
offset, and emits one `R_ARM_THM_JUMP24` relocation to each exact API. The
1,776-byte source object has SHA-256
`e8fc442adba6730f9d00ee07a2b67e57f711831b4f2f92328c1ad620349390a6`
and no ELF import.

## Fixed source-owned provider boundary

The adapter preserves upstream lazy initialization, recursive take/give,
infinite lock wait, deletion, result mapping, and double-checked critical
section behavior. Its only target dependencies are six canonical Thumb
entries already redirected to reviewed source providers:

| Address | Provider |
|---|---|
| `0x004420D1` | `vPortEnterCritical` |
| `0x004420E9` | `vPortExitCritical` |
| `0x004416D7` | `xQueueCreateMutex` |
| `0x00441751` | `xQueueTakeMutexRecursive` |
| `0x00441711` | `xQueueGiveMutexRecursive` |
| `0x00441EA3` | `vQueueDelete` |

Their maintained source ancestry is FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The manifest also pins the exact
component-local queue, queue-delete, and scheduler-port source identities
which own those canonical entries.

The fixed calls make the object ELF-closed; they do not prove live scheduler
state, critical-nesting RAM, heap state, recursive owner behavior, or that a
future production image keeps the same address routes.

## Hostile-input policy

The host fixture verifies successful and failed lazy creation, idempotent
initialization, full `UINT32_MAX` wait forwarding, take/give result mapping,
deletion, and provider call counts. Null descriptors and malformed
initialized/null-handle states return invalid without invoking FreeRTOS.
Failed lazy allocation leaves the descriptor uninitialized; `lv_mutex_init`
still returns success as the authenticated LVGL source does. Deletion clears
the stale handle in addition to the initialization flag.

Those null/stale-handle guards deliberately replace upstream fault/assert
paths. Failure diagnostics are not emitted because `lv_log_add` is itself an
unclosed residual provider. The functional return/state boundary is explicit
and ASan/UBSan-clean; diagnostic side-effect equivalence is not claimed.

## Excluded boundary and reproduction

`lv_thread_init` and `lv_thread_delete` remain excluded because their task
creation/deletion closure crosses TCB, stack allocation, scheduler, and RAM
placement. The four `lv_thread_sync_*` APIs remain excluded because their
structure and provider graph change with `LV_USE_FREERTOS_TASK_NOTIFY`.
Neither mode is selected by preference.

From `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py \
  --write-manifest tools/manifests/g2-lvgl-nema-link-admission.json
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_mutex_provider
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
```

No authorized physical target identity, transport, scheduler trace, heap
snapshot, critical-nesting capture, GPU trace, framebuffer capture, or display
observation was supplied. Runtime concurrency and complete rendering remain
blocked by unavailable physical evidence.

A subsequent independently audited FPv5-D16 math provider moves the current
residual from 31 to 27; see `g2-lvgl-math-dp-provider-source-admission.md`.
The 31-symbol result above remains the historical output of this mutex tranche.
