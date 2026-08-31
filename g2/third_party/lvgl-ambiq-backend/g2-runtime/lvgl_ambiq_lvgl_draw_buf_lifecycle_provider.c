/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounded transcription of lv_draw_buf_destroy from LVGL commit
 * 344c7c318047b7348e1be8572a9fd4260c251cfa.  Handler ownership stays in the
 * descriptor.  A malformed allocated descriptor without handlers fails
 * closed instead of dereferencing null after the upstream diagnostic.
 */

#include "lvgl_ambiq_lvgl_draw_buf_lifecycle_provider.h"

void lv_draw_buf_destroy(lv_draw_buf_t * draw_buf)
{
    const lv_draw_buf_handlers_t * handlers;

    if(draw_buf == NULL) return;
    if((draw_buf->header.flags & LV_IMAGE_FLAGS_ALLOCATED) == 0U) return;

    handlers = draw_buf->handlers;
    if(handlers == NULL) return;
    if(handlers->buf_free_cb != NULL) {
        handlers->buf_free_cb(draw_buf->unaligned_data);
    }
    lv_free(draw_buf);
}
