/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounded transcription of lv_freetype_outline_add_event from authenticated
 * LVGL commit 344c7c318047b7348e1be8572a9fd4260c251cfa.  LVGL 9.3-development
 * stores only the callback; filter and user_data are intentionally ignored.
 * A missing FreeType context fails closed instead of dereferencing null.
 */

#include "lvgl_ambiq_lvgl_freetype_event_provider.h"
#include "src/core/lv_global.h"
#include "src/libs/freetype/lv_freetype_private.h"

#ifndef OPEN_CFW_LVGL_FREETYPE_CONTEXT
#define OPEN_CFW_LVGL_FREETYPE_CONTEXT() (LV_GLOBAL_DEFAULT()->ft_context)
#endif

void lv_freetype_outline_add_event(
    lv_event_cb_t event_cb,
    lv_event_code_t filter,
    void * user_data
)
{
    lv_freetype_context_t * ctx;

    LV_UNUSED(filter);
    LV_UNUSED(user_data);

    ctx = OPEN_CFW_LVGL_FREETYPE_CONTEXT();
    if(ctx == NULL) return;
    ctx->event_cb = event_cb;
}

#undef OPEN_CFW_LVGL_FREETYPE_CONTEXT
