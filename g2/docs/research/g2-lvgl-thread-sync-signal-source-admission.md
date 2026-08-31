# G2 LVGL thread-sync signal source admission

## Scope

This note bounds an isolated exact-ABI `lv_thread_sync_signal` provider for the
task-notification FreeRTOS branch selected by the recovered G2 LVGL
configuration.  It does not route the provider into the production overlay or
qualify live scheduler behavior.

## Configuration and source identity

The recovered configuration selects `LV_OS_FREERTOS`, does not define
`LV_KCONFIG_PRESENT`, and does not override `LV_USE_FREERTOS_TASK_NOTIFY`.
Authenticated LVGL commit `344c7c318047b7348e1be8572a9fd4260c251cfa`
therefore selects the upstream default value `1`.  The target ABI probe pins a
12-byte synchronization object with `xIsInitialized`, `xSyncSignal`, and
`xTaskToNotify` at offsets 0, 4, and 8.

The provider transcribes the authenticated lazy initialization, double-checked
critical section, pending-signal path, waiter handoff, and ignored notification
result.  `xTaskNotifyGive` is expanded exactly to `xTaskGenericNotify(task, 0,
0, eIncrement, NULL)`.

## Fixed provider boundary

The target object has no ELF undefined symbol.  Its only external effects are
three exact Thumb calls:

| Address | Source-owned API |
|---|---|
| `0x004420D1` | `vPortEnterCritical` |
| `0x004420E9` | `vPortExitCritical` |
| `0x00455C49` | `xTaskGenericNotify` |

The critical-section entries are already pinned by the LVGL mutex admission.
The notification entry is backed by the maintained FreeRTOS V10.5.1 provider
from commit `def7d2df2b0506d3d249334974f51e427c17a41c`, which owns the recovered
G2 task-notification TCB/scheduler ABI.

## Hostile-input and admission boundary

Null input fails before fixed calls.  Host tests cover lazy initialization,
already-pending signals, waiter notification with an ignored failure result,
the double-check race, and noncanonical nonzero initialized state.  These are
sanitizer-clean source tests, not evidence of a running scheduler.

Production routing and hardware qualification remain false.  Live critical
nesting, task lifetime, TCB validity, scheduler/list state, interrupt masking,
RAM placement, fixed-entry collision, wakeup behavior, and the paired
`lv_thread_sync_wait` implementation remain unqualified.
