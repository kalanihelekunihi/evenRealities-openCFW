/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_LVGL_AMBIQ_LVGL_MUTEX_PROVIDER_H
#define OPENCFW_LVGL_AMBIQ_LVGL_MUTEX_PROVIDER_H

#include <stdint.h>

typedef enum open_cfw_lvgl_mutex_result {
    OPEN_CFW_LVGL_MUTEX_INVALID = 0,
    OPEN_CFW_LVGL_MUTEX_OK = 1
} open_cfw_lvgl_mutex_result;

typedef struct open_cfw_lvgl_mutex {
    int32_t initialized;
    void * handle;
} open_cfw_lvgl_mutex;

open_cfw_lvgl_mutex_result lv_mutex_init(open_cfw_lvgl_mutex * mutex);
open_cfw_lvgl_mutex_result lv_mutex_lock(open_cfw_lvgl_mutex * mutex);
open_cfw_lvgl_mutex_result lv_mutex_unlock(open_cfw_lvgl_mutex * mutex);
open_cfw_lvgl_mutex_result lv_mutex_delete(open_cfw_lvgl_mutex * mutex);

#endif /* OPENCFW_LVGL_AMBIQ_LVGL_MUTEX_PROVIDER_H */
