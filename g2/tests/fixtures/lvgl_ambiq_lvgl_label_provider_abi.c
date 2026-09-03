/* SPDX-License-Identifier: MIT */
#include "../../third_party/lvgl/src/draw/lv_draw_label_private.h"

void open_cfw_lvgl_label_probe(lv_draw_task_t * task, const lv_draw_label_dsc_t * dsc,
                               const lv_area_t * coords, lv_draw_glyph_cb_t glyph_cb)
{
    lv_draw_label_iterate_characters(task, dsc, coords, glyph_cb);
}
