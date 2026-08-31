/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_DRAW_BUF_SHAPE_PROVIDER_H
#define OPEN_CFW_LVGL_AMBIQ_DRAW_BUF_SHAPE_PROVIDER_H

#include "src/draw/lv_draw_buf_private.h"

#ifdef __cplusplus
extern "C" {
#endif

lv_draw_buf_t * lv_draw_buf_create(
    uint32_t w,
    uint32_t h,
    lv_color_format_t cf,
    uint32_t stride
);
lv_draw_buf_t * lv_draw_buf_reshape(
    lv_draw_buf_t * draw_buf,
    lv_color_format_t cf,
    uint32_t w,
    uint32_t h,
    uint32_t stride
);

#ifdef __cplusplus
}
#endif

#endif
