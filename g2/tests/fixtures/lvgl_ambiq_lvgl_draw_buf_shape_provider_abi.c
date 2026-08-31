/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_draw_buf_shape_provider.h"

lv_draw_buf_t * open_cfw_lvgl_draw_buf_create_probe(
    uint32_t w,
    uint32_t h,
    lv_color_format_t cf,
    uint32_t stride
)
{
    return lv_draw_buf_create(w, h, cf, stride);
}

lv_draw_buf_t * open_cfw_lvgl_draw_buf_reshape_probe(
    lv_draw_buf_t * draw_buf,
    lv_color_format_t cf,
    uint32_t w,
    uint32_t h,
    uint32_t stride
)
{
    return lv_draw_buf_reshape(draw_buf, cf, w, h, stride);
}
