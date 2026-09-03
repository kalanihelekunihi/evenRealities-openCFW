# G2 LVGL thread and sync OSAL source admission

## Scope

This note bounds an isolated exact-ABI provider for `lv_thread_init`,
`lv_thread_delete`, and the four task-notification sync operations selected by
the recovered G2 LVGL configuration. It does not route the provider into the
production overlay or qualify live scheduler behavior.

## Configuration and source identity

The recovered configuration selects `LV_OS_FREERTOS`, does not define
`LV_KCONFIG_PRESENT`, and does not override `LV_USE_FREERTOS_TASK_NOTIFY`.
Authenticated LVGL commit `344c7c318047b7348e1be8572a9fd4260c251cfa`
therefore selects the upstream default value `1`. The target ABI probe pins a
12-byte synchronization object with `xIsInitialized`, `xSyncSignal`, and
`xTaskToNotify` at offsets 0, 4, and 8, plus a 12-byte thread object with the
callback, argument, and task handle at those same respective offsets.

The provider transcribes the authenticated dynamic thread creation, private
runner, self-delete, explicit deletion, lazy synchronization initialization,
double-checked critical section, pending-signal path, waiter handoff, and
ignored notification result. `xTaskNotifyGive` is expanded exactly to
`xTaskGenericNotify(task, 0, 0, eIncrement, NULL)`, and waiting uses the exact
upstream `ulTaskNotifyTake(pdTRUE, portMAX_DELAY)` ABI.

## Fixed provider boundary

The target object has no ELF undefined symbol. Its external effects are eight
exact Thumb calls:

| Address | Source-owned API |
|---|---|
| `0x004420D1` | `vPortEnterCritical` |
| `0x004420E9` | `vPortExitCritical` |
| `0x004548BB` | `xTaskCreate` |
| `0x00454AAF` | `vTaskDelete` |
| `0x0045589D` | `xTaskGetCurrentTaskHandle` |
| `0x00455FA9` | `prvAddCurrentTaskToDelayedList` |
| `0x00455C49` | `xTaskGenericNotify` |
| `0x004420BD` | `vPortYield` |

The critical-section, task-create/delete, current-task, notification,
delayed-list, and yield entries are backed by maintained FreeRTOS V10.5.1
source and the recovered G2 TCB patch. The provider now implements the exact
index-zero `ulTaskNotifyTake(pdTRUE, portMAX_DELAY)` behavior in maintained C:
it marks an empty notification slot waiting, inserts the current task into the
indefinite-delay list, yields, then atomically consumes the notification and
returns the slot to not-waiting. There is no retained task-take body.

## Hostile-input and admission boundary

Null objects, names, callbacks, handles, zero-depth stacks, oversized stacks,
and invalid priorities fail before fixed calls. Host tests cover successful and
failed thread creation, exact stack-byte-to-word conversion, runner callback and
self-delete behavior, explicit delete, lazy synchronization initialization,
already-pending signals, waiter notification with an ignored failure result,
the double-check race, and noncanonical nonzero initialized state. These are
sanitizer-clean source tests, not evidence of a running scheduler.

Production routing and hardware qualification remain false.  Live critical
nesting, task lifetime, TCB validity, scheduler/list state, interrupt masking,
RAM placement, fixed-entry collision, task allocation, and wakeup behavior
remain unqualified. The retained task-take seam remains a software-ownership
gap; it is not reclassified as a hardware blocker.
