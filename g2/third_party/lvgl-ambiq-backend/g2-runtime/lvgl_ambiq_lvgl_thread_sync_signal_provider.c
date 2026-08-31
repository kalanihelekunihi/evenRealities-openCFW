/* SPDX-License-Identifier: MIT */
/* Exact-ABI task-notification-mode LVGL thread-sync signal provider. */

#include "lvgl_ambiq_lvgl_thread_sync_signal_provider.h"

#include <stddef.h>
#include <stdint.h>

typedef int32_t open_cfw_base_type;
typedef uint32_t open_cfw_ubase_type;

enum {
    OPEN_CFW_FALSE = 0,
    OPEN_CFW_TRUE = 1,
    OPEN_CFW_NOTIFY_INCREMENT = 2
};

#if defined(__arm__) || defined(__thumb__)
_Static_assert(sizeof(void *) == 4U, "G2 pointer ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_thread_sync_result) == 1U,
               "G2 short-enum result ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_thread_sync) == 12U,
               "G2 notify-mode lv_thread_sync_t ABI changed");
_Static_assert(offsetof(open_cfw_lvgl_thread_sync, initialized) == 0U,
               "G2 sync initialized offset changed");
_Static_assert(offsetof(open_cfw_lvgl_thread_sync, signal) == 4U,
               "G2 sync signal offset changed");
_Static_assert(offsetof(open_cfw_lvgl_thread_sync, task_to_notify) == 8U,
               "G2 sync task offset changed");
#endif

#ifndef OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL
typedef void (*open_cfw_enter_critical_fn)(void);
#define OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL() \
    (((open_cfw_enter_critical_fn)(uintptr_t)0x004420D1U)())
#endif

#ifndef OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL
typedef void (*open_cfw_exit_critical_fn)(void);
#define OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL() \
    (((open_cfw_exit_critical_fn)(uintptr_t)0x004420E9U)())
#endif

#ifndef OPEN_CFW_LVGL_SYNC_TASK_NOTIFY
typedef open_cfw_base_type (*open_cfw_task_notify_fn)(
    void *, open_cfw_ubase_type, open_cfw_ubase_type,
    open_cfw_base_type, open_cfw_ubase_type *
);
#define OPEN_CFW_LVGL_SYNC_TASK_NOTIFY(task, index, value, action, previous) \
    (((open_cfw_task_notify_fn)(uintptr_t)0x00455C49U)( \
        (task), (index), (value), (action), (previous)))
#endif

static void open_cfw_lvgl_sync_initialize_if_needed(
    open_cfw_lvgl_thread_sync * sync
)
{
    if(sync->initialized != OPEN_CFW_FALSE) return;

    OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL();
    if(sync->initialized == OPEN_CFW_FALSE) {
        sync->initialized = OPEN_CFW_TRUE;
        sync->signal = OPEN_CFW_FALSE;
        sync->task_to_notify = NULL;
    }
    OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL();
}

__attribute__((visibility("default"), used, noinline))
open_cfw_lvgl_thread_sync_result lv_thread_sync_signal(
    open_cfw_lvgl_thread_sync * sync
)
{
    void * task_to_notify;

    if(sync == NULL) return OPEN_CFW_LVGL_THREAD_SYNC_INVALID;
    open_cfw_lvgl_sync_initialize_if_needed(sync);

    OPEN_CFW_LVGL_SYNC_ENTER_CRITICAL();
    task_to_notify = sync->task_to_notify;
    sync->task_to_notify = NULL;
    if(task_to_notify == NULL) sync->signal = OPEN_CFW_TRUE;
    OPEN_CFW_LVGL_SYNC_EXIT_CRITICAL();

    if(task_to_notify != NULL) {
        (void)OPEN_CFW_LVGL_SYNC_TASK_NOTIFY(
            task_to_notify, 0U, 0U, OPEN_CFW_NOTIFY_INCREMENT, NULL
        );
    }
    return OPEN_CFW_LVGL_THREAD_SYNC_OK;
}
