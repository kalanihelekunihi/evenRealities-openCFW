/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_LVGL_AMBIQ_THREAD_SYNC_SIGNAL_PROVIDER_H
#define OPENCFW_LVGL_AMBIQ_THREAD_SYNC_SIGNAL_PROVIDER_H

#include <stdint.h>

typedef enum open_cfw_lvgl_thread_sync_result {
    OPEN_CFW_LVGL_THREAD_SYNC_INVALID = 0,
    OPEN_CFW_LVGL_THREAD_SYNC_OK = 1
} open_cfw_lvgl_thread_sync_result;

typedef struct open_cfw_lvgl_thread_sync {
    int32_t initialized;
    int32_t signal;
    void * task_to_notify;
} open_cfw_lvgl_thread_sync;

open_cfw_lvgl_thread_sync_result lv_thread_sync_signal(
    open_cfw_lvgl_thread_sync * sync
);

#endif
