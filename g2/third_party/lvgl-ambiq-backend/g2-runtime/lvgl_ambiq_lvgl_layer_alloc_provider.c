/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounded transcription of lv_draw_layer_alloc_buf from authenticated LVGL
 * commit 344c7c318047b7348e1be8572a9fd4260c251cfa. The recovered G2 build has
 * LV_DRAW_LAYER_MAX_MEMORY == 0 and LV_LOG_LEVEL == LV_LOG_LEVEL_WARN.
 */

#include <limits.h>
#include <stddef.h>
#include <stdint.h>

#include "lvgl_ambiq_lvgl_layer_alloc_provider.h"
#include "src/core/lv_global.h"
#include "src/draw/lv_draw_buf_private.h"
#include "src/misc/lv_area_private.h"
#include "src/misc/lv_log.h"
#include "src/stdlib/lv_string.h"

#if LV_DRAW_LAYER_MAX_MEMORY != 0
#error "G2 layer provider requires the recovered unlimited layer policy"
#endif

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(lv_global_t, draw_info) == 0x13CU,
               "G2 draw-info offset changed");
_Static_assert(offsetof(lv_layer_t, buf_area) == 0x04U,
               "G2 layer buffer-area offset changed");
_Static_assert(offsetof(lv_layer_t, color_format) == 0x14U,
               "G2 layer color-format offset changed");
_Static_assert(offsetof(lv_layer_t, draw_buf) == 0x00U,
               "G2 layer draw-buffer offset changed");
#endif

static bool color_format_has_alpha(lv_color_format_t format)
{
    switch(format) {
        case LV_COLOR_FORMAT_A1:
        case LV_COLOR_FORMAT_A2:
        case LV_COLOR_FORMAT_A4:
        case LV_COLOR_FORMAT_A8:
        case LV_COLOR_FORMAT_I1:
        case LV_COLOR_FORMAT_I2:
        case LV_COLOR_FORMAT_I4:
        case LV_COLOR_FORMAT_I8:
        case LV_COLOR_FORMAT_RGB565A8:
        case LV_COLOR_FORMAT_ARGB8565:
        case LV_COLOR_FORMAT_ARGB8888:
        case LV_COLOR_FORMAT_AL88:
        case LV_COLOR_FORMAT_ARGB2222:
        case LV_COLOR_FORMAT_ARGB1555:
        case LV_COLOR_FORMAT_ARGB4444:
            return true;
        default:
            return false;
    }
}

static bool clear_full_draw_buf(lv_draw_buf_t * draw_buf)
{
    uint64_t byte_count;
    uint64_t palette_bytes;
    uint8_t * pixels;

    if(draw_buf == NULL || draw_buf->data == NULL) return false;
    byte_count = (uint64_t)draw_buf->header.h * draw_buf->header.stride;
    palette_bytes =
        (uint64_t)LV_COLOR_INDEXED_PALETTE_SIZE(draw_buf->header.cf) *
        sizeof(lv_color32_t);
    if(byte_count > SIZE_MAX || palette_bytes > SIZE_MAX ||
       palette_bytes + byte_count > draw_buf->data_size) {
        return false;
    }
    pixels = (uint8_t *)draw_buf->data + (size_t)palette_bytes;
    lv_memset(pixels, 0, (size_t)byte_count);
    lv_draw_buf_flush_cache(draw_buf, NULL);
    return true;
}

void * lv_draw_layer_alloc_buf(lv_layer_t * layer)
{
    lv_draw_global_info_t * draw_info;
    const lv_draw_buf_handlers_t * handlers;
    int32_t width;
    int32_t height;
    uint32_t stride;
    uint64_t layer_size;

    if(layer == NULL) return NULL;
    if(layer->draw_buf != NULL) return layer->draw_buf->data;

    width = lv_area_get_width(&layer->buf_area);
    height = lv_area_get_height(&layer->buf_area);
    if(width <= 0 || height <= 0) return NULL;

    handlers = &LV_GLOBAL_DEFAULT()->draw_buf_handlers;
    if(handlers->width_to_stride_cb == NULL) return NULL;
    stride = handlers->width_to_stride_cb((uint32_t)width, layer->color_format);
    layer_size = (uint64_t)(uint32_t)height * stride;
    if(stride == 0U || layer_size > UINT32_MAX) return NULL;

    layer->draw_buf = lv_draw_buf_create((uint32_t)width, (uint32_t)height,
                                         layer->color_format, 0U);
    if(layer->draw_buf == NULL) {
        LV_LOG_WARN("Allocating layer buffer failed. Try later");
        return NULL;
    }

    draw_info = &LV_GLOBAL_DEFAULT()->draw_info;
    if(layer_size > UINT32_MAX - draw_info->used_memory_for_layers) {
        lv_draw_buf_destroy(layer->draw_buf);
        layer->draw_buf = NULL;
        return NULL;
    }
    draw_info->used_memory_for_layers += (uint32_t)layer_size;

    if(color_format_has_alpha(layer->color_format) &&
       !clear_full_draw_buf(layer->draw_buf)) {
        draw_info->used_memory_for_layers -= (uint32_t)layer_size;
        lv_draw_buf_destroy(layer->draw_buf);
        layer->draw_buf = NULL;
        return NULL;
    }
    return layer->draw_buf->data;
}
