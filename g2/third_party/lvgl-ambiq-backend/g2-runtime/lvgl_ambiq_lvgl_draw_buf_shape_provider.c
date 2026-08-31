/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounded transcription of lv_draw_buf_create and lv_draw_buf_reshape from
 * authenticated LVGL commit 344c7c318047b7348e1be8572a9fd4260c251cfa.
 * The retained Ambiq initializer owns the default callbacks.  This provider
 * validates their presence and all public 16/32-bit size boundaries before an
 * indirect call or descriptor mutation.
 */

#include <limits.h>
#include <stdbool.h>
#include <stdint.h>

#include "lvgl_ambiq_lvgl_draw_buf_shape_provider.h"
#include "src/core/lv_global.h"
#include "src/stdlib/lv_mem.h"

#ifndef OPEN_CFW_LVGL_DRAW_BUF_DEFAULT_HANDLERS
#define OPEN_CFW_LVGL_DRAW_BUF_DEFAULT_HANDLERS() \
    (&LV_GLOBAL_DEFAULT()->draw_buf_handlers)
#endif

static bool open_cfw_draw_buf_size(
    uint32_t w,
    uint32_t h,
    lv_color_format_t cf,
    uint32_t stride,
    uint32_t * size_out
)
{
    uint64_t size;

    if(size_out == NULL || w == 0U || h == 0U) return false;
    if(w > UINT16_MAX || h > UINT16_MAX || stride == 0U || stride > UINT16_MAX) {
        return false;
    }

    size = (uint64_t)stride * h;
    if(cf == LV_COLOR_FORMAT_RGB565A8) {
        size += (uint64_t)(stride / 2U) * h;
    }
    else if(LV_COLOR_FORMAT_IS_INDEXED(cf)) {
        size += (uint64_t)LV_COLOR_INDEXED_PALETTE_SIZE(cf) * sizeof(lv_color32_t);
    }
    if(size == 0U || size > UINT32_MAX) return false;
    *size_out = (uint32_t)size;
    return true;
}

lv_draw_buf_t * lv_draw_buf_create(
    uint32_t w,
    uint32_t h,
    lv_color_format_t cf,
    uint32_t stride
)
{
    const lv_draw_buf_handlers_t * handlers;
    lv_draw_buf_t * draw_buf;
    uint32_t size;
    void * unaligned;
    void * aligned;

    handlers = OPEN_CFW_LVGL_DRAW_BUF_DEFAULT_HANDLERS();
    if(handlers == NULL || handlers->buf_malloc_cb == NULL ||
       handlers->buf_free_cb == NULL || handlers->align_pointer_cb == NULL) {
        return NULL;
    }
    draw_buf = lv_malloc_zeroed(sizeof(*draw_buf));
    if(draw_buf == NULL) return NULL;
    if(stride == 0U) {
        if(handlers->width_to_stride_cb == NULL) {
            lv_free(draw_buf);
            return NULL;
        }
        stride = handlers->width_to_stride_cb(w, cf);
    }
    if(!open_cfw_draw_buf_size(w, h, cf, stride, &size)) {
        lv_free(draw_buf);
        return NULL;
    }
    unaligned = handlers->buf_malloc_cb(size, cf);
    if(unaligned == NULL) {
        lv_free(draw_buf);
        return NULL;
    }
    aligned = handlers->align_pointer_cb(unaligned, cf);
    if(aligned == NULL) {
        handlers->buf_free_cb(unaligned);
        lv_free(draw_buf);
        return NULL;
    }

    draw_buf->header.w = w;
    draw_buf->header.h = h;
    draw_buf->header.cf = cf;
    draw_buf->header.flags = LV_IMAGE_FLAGS_MODIFIABLE | LV_IMAGE_FLAGS_ALLOCATED;
    draw_buf->header.stride = stride;
    draw_buf->header.magic = LV_IMAGE_HEADER_MAGIC;
    draw_buf->data = aligned;
    draw_buf->unaligned_data = unaligned;
    draw_buf->data_size = size;
    draw_buf->handlers = handlers;
    return draw_buf;
}

lv_draw_buf_t * lv_draw_buf_reshape(
    lv_draw_buf_t * draw_buf,
    lv_color_format_t cf,
    uint32_t w,
    uint32_t h,
    uint32_t stride
)
{
    const lv_draw_buf_handlers_t * handlers;
    uint32_t size;

    if(draw_buf == NULL) return NULL;
    if(cf == LV_COLOR_FORMAT_UNKNOWN) cf = draw_buf->header.cf;
    if(stride == 0U) {
        handlers = OPEN_CFW_LVGL_DRAW_BUF_DEFAULT_HANDLERS();
        if(handlers == NULL || handlers->width_to_stride_cb == NULL) return NULL;
        stride = handlers->width_to_stride_cb(w, cf);
    }
    if(!open_cfw_draw_buf_size(w, h, cf, stride, &size)) return NULL;
    if(size > draw_buf->data_size) return NULL;

    draw_buf->header.cf = cf;
    draw_buf->header.w = w;
    draw_buf->header.h = h;
    draw_buf->header.stride = stride;
    return draw_buf;
}

#undef OPEN_CFW_LVGL_DRAW_BUF_DEFAULT_HANDLERS
