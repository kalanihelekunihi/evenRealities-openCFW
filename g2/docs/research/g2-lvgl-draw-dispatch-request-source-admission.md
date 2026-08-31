# G2 LVGL draw-dispatch request source admission

## Scope

This note bounds the isolated `lv_draw_dispatch_request` provider required by
the retained Ambiq draw unit.  It neither provides the FreeRTOS condition
implementation nor registers a production route.

## Authenticated behavior

LVGL commit `344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`, defines the OS-enabled function in
`src/draw/lv_draw.c`.  It calls `lv_thread_sync_signal` twice with the address of
`LV_GLOBAL_DEFAULT()->draw_info.sync` and ignores both results.  The local
provider preserves the exact pointer, count, order, and result handling.  It is
compiled only for the recovered `LV_OS_FREERTOS` ABI.

The host oracle fills the global object with nonzero hostile state, makes the
first signal return failure, and verifies that the exact synchronization object
is still signaled twice.  The function has no public input pointer or size and
performs no arithmetic or direct MMIO access.

## Link boundary

The Cortex-M55 object exports only `lv_draw_dispatch_request`.  Its exact
imports are `lv_global` and `lv_thread_sync_signal`. `lv_global` is owned by
the isolated global-storage provider. The subsequent task-notification-mode
admission now provides `lv_thread_sync_signal`, and the three-provider aggregate
is undefined-symbol-free. This does not imply that the live scheduler is
qualified. The retained consumer and every target relocation are pinned by the
component analyzer.

## Admission boundary

This is source/ABI admission only. The live `lv_global` initializer, sync
object lifetime, task-notification scheduler state,
critical-section behavior, RAM placement, symbol collision, and wakeup behavior
remain unqualified.  Production routing and hardware qualification are false.
