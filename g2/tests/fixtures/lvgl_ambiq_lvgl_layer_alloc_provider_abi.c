/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_layer_alloc_provider.h"

void * open_cfw_lvgl_layer_alloc_probe(lv_layer_t * layer)
{
    return lv_draw_layer_alloc_buf(layer);
}
