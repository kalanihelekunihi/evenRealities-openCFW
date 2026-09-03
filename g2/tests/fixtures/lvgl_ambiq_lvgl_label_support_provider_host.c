/* SPDX-License-Identifier: MIT */
#include "../../third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_label_support_provider.h"

#include <assert.h>
#include <limits.h>

int main(void)
{
    lv_area_t holder = {0, 0, 99, 99};
    lv_area_t overlap = {90, 90, 110, 110};
    lv_area_t outside = {100, 0, 110, 10};
    lv_area_t corner = {0, 0, 0, 0};
    lv_area_t rounded_inside = {20, 20, 30, 30};
    lv_area_t extreme = {INT32_MAX - 1, INT32_MAX - 1, INT32_MAX, INT32_MAX};
    lv_point_t point = {0, 0};
    lv_color_t color;

    assert(!lv_area_is_out(&overlap, &holder, 0));
    assert(lv_area_is_out(&outside, &holder, 0));
    assert(lv_area_is_out(&corner, &holder, 20));
    assert(!lv_area_is_out(&rounded_inside, &holder, 20));
    assert(lv_area_is_out(&holder, &holder, 20));
    assert(lv_area_is_out(NULL, &holder, 0));
    assert(lv_area_is_out(&holder, NULL, 0));
    assert(lv_area_is_out(&extreme, &extreme, INT32_MAX));

    lv_point_set(&point, -7, 13);
    assert(point.x == -7 && point.y == 13);
    lv_point_set(NULL, 1, 2);

    color = lv_color_make(1U, 2U, 3U);
    assert(color.red == 1U && color.green == 2U && color.blue == 3U);
    color = lv_color_black();
    assert(color.red == 0U && color.green == 0U && color.blue == 0U);
    return 0;
}
