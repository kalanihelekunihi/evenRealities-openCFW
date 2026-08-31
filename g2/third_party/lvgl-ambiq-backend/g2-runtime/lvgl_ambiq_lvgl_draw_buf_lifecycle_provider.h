/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_DRAW_BUF_LIFECYCLE_PROVIDER_H
#define OPEN_CFW_LVGL_AMBIQ_DRAW_BUF_LIFECYCLE_PROVIDER_H

#include "lvgl.h"
#include "src/draw/lv_draw_buf_private.h"

#ifdef __cplusplus
extern "C" {
#endif

void lv_draw_buf_destroy(lv_draw_buf_t * draw_buf);

#ifdef __cplusplus
}
#endif

#endif
