/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_DRAW_TASK_PROVIDER_H
#define OPEN_CFW_LVGL_AMBIQ_DRAW_TASK_PROVIDER_H

#include "src/draw/lv_draw_private.h"

#ifdef __cplusplus
extern "C" {
#endif

lv_draw_task_t * lv_draw_get_available_task(lv_layer_t * layer,
                                             lv_draw_task_t * previous,
                                             uint8_t draw_unit_id);

#ifdef __cplusplus
}
#endif

#endif
