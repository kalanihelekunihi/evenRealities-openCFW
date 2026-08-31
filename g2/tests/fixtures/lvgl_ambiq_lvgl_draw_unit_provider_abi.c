/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_draw_unit_provider.h"

void * open_cfw_lvgl_draw_create_unit_probe(size_t size)
{
    return lv_draw_create_unit(size);
}
