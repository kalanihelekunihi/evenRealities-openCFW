/* SPDX-License-Identifier: MIT */
#include "src/osal/lv_os.h"

_Static_assert(LV_USE_FREERTOS_TASK_NOTIFY == 1,
               "G2 LVGL task-notification mode changed");
_Static_assert(sizeof(void *) == 4U, "G2 pointer ABI changed");
_Static_assert(sizeof(lv_result_t) == 1U, "G2 short-enum ABI changed");
_Static_assert(sizeof(lv_thread_sync_t) == 12U, "G2 sync ABI changed");
_Static_assert(__builtin_offsetof(lv_thread_sync_t, xIsInitialized) == 0U,
               "G2 sync initialized offset changed");
_Static_assert(__builtin_offsetof(lv_thread_sync_t, xSyncSignal) == 4U,
               "G2 sync signal offset changed");
_Static_assert(__builtin_offsetof(lv_thread_sync_t, xTaskToNotify) == 8U,
               "G2 sync task offset changed");

lv_result_t open_cfw_lvgl_thread_sync_signal_probe(lv_thread_sync_t * sync)
{
    return lv_thread_sync_signal(sync);
}
