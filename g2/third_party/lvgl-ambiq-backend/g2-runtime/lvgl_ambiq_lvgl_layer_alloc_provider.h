/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_LAYER_ALLOC_PROVIDER_H
#define OPEN_CFW_LVGL_AMBIQ_LAYER_ALLOC_PROVIDER_H

#include "src/draw/lv_draw_private.h"

#ifdef __cplusplus
extern "C" {
#endif

void * lv_draw_layer_alloc_buf(lv_layer_t * layer);

#ifdef __cplusplus
}
#endif

#endif
