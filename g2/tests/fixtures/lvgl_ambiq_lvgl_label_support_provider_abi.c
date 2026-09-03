/* SPDX-License-Identifier: MIT */
#include "../../third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_label_support_provider.h"

bool open_cfw_lvgl_label_support_probe(const lv_area_t * area, const lv_area_t * holder,
                                       lv_point_t * point, int32_t x, int32_t y)
{
    lv_color_t black = lv_color_black();
    lv_color_t made = lv_color_make(1U, 2U, 3U);
    lv_point_set(point, x, y);
    return lv_area_is_out(area, holder, 0) || black.red != 0U || made.blue != 3U;
}
