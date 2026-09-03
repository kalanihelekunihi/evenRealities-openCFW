/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_draw_task_provider.h"

lv_draw_task_t * open_cfw_lvgl_draw_task_probe(lv_layer_t * layer,
                                                lv_draw_task_t * previous,
                                                uint8_t draw_unit_id)
{
    return lv_draw_get_available_task(layer, previous, draw_unit_id);
}
