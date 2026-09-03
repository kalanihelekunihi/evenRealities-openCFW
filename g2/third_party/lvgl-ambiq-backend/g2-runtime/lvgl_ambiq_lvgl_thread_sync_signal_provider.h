/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_LVGL_AMBIQ_THREAD_SYNC_SIGNAL_PROVIDER_H
#define OPENCFW_LVGL_AMBIQ_THREAD_SYNC_SIGNAL_PROVIDER_H

#include <stddef.h>
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

typedef enum open_cfw_lvgl_thread_priority {
    OPEN_CFW_LVGL_THREAD_PRIO_LOWEST = 0,
    OPEN_CFW_LVGL_THREAD_PRIO_LOW = 1,
    OPEN_CFW_LVGL_THREAD_PRIO_MID = 2,
    OPEN_CFW_LVGL_THREAD_PRIO_HIGH = 3,
    OPEN_CFW_LVGL_THREAD_PRIO_HIGHEST = 4
} open_cfw_lvgl_thread_priority;

typedef struct open_cfw_lvgl_thread {
    void (*start_routine)(void *);
    void * task_argument;
    void * task_handle;
} open_cfw_lvgl_thread;

open_cfw_lvgl_thread_sync_result lv_thread_init(
    open_cfw_lvgl_thread * thread,
    const char * name,
    open_cfw_lvgl_thread_priority priority,
    void (*callback)(void *),
    size_t stack_size,
    void * user_data
);
open_cfw_lvgl_thread_sync_result lv_thread_delete(
    open_cfw_lvgl_thread * thread
);

open_cfw_lvgl_thread_sync_result lv_thread_sync_signal(
    open_cfw_lvgl_thread_sync * sync
);
open_cfw_lvgl_thread_sync_result lv_thread_sync_init(
    open_cfw_lvgl_thread_sync * sync
);
open_cfw_lvgl_thread_sync_result lv_thread_sync_wait(
    open_cfw_lvgl_thread_sync * sync
);
open_cfw_lvgl_thread_sync_result lv_thread_sync_delete(
    open_cfw_lvgl_thread_sync * sync
);

#endif
