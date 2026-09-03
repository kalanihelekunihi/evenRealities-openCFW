/* SPDX-License-Identifier: MIT */
#include "src/osal/lv_os.h"

_Static_assert(LV_USE_FREERTOS_TASK_NOTIFY == 1,
               "G2 LVGL task-notification mode changed");
_Static_assert(sizeof(void *) == 4U, "G2 pointer ABI changed");
_Static_assert(sizeof(lv_result_t) == 1U, "G2 short-enum ABI changed");
_Static_assert(sizeof(lv_thread_sync_t) == 12U, "G2 sync ABI changed");
_Static_assert(sizeof(lv_thread_t) == 12U, "G2 thread ABI changed");
_Static_assert(sizeof(lv_thread_prio_t) == 1U, "G2 thread priority ABI changed");
_Static_assert(__builtin_offsetof(lv_thread_t, pvStartRoutine) == 0U,
               "G2 thread callback offset changed");
_Static_assert(__builtin_offsetof(lv_thread_t, pTaskArg) == 4U,
               "G2 thread argument offset changed");
_Static_assert(__builtin_offsetof(lv_thread_t, xTaskHandle) == 8U,
               "G2 thread handle offset changed");
_Static_assert(__builtin_offsetof(lv_thread_sync_t, xIsInitialized) == 0U,
               "G2 sync initialized offset changed");
_Static_assert(__builtin_offsetof(lv_thread_sync_t, xSyncSignal) == 4U,
               "G2 sync signal offset changed");
_Static_assert(__builtin_offsetof(lv_thread_sync_t, xTaskToNotify) == 8U,
               "G2 sync task offset changed");

lv_result_t open_cfw_lvgl_thread_sync_signal_probe(lv_thread_sync_t * sync)
{
    lv_result_t result = lv_thread_sync_init(sync);
    result = (lv_result_t)(result & lv_thread_sync_wait(sync));
    result = (lv_result_t)(result & lv_thread_sync_signal(sync));
    result = (lv_result_t)(result & lv_thread_sync_delete(sync));
    return result;
}

lv_result_t open_cfw_lvgl_thread_probe(
    lv_thread_t * thread, const char * name, lv_thread_prio_t priority,
    void (*callback)(void *), size_t stack_size, void * user_data
)
{
    lv_result_t result = lv_thread_init(
        thread, name, priority, callback, stack_size, user_data
    );
    return (lv_result_t)(result & lv_thread_delete(thread));
}
