/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_draw_buf_lifecycle_provider.h"

_Static_assert(sizeof(lv_draw_buf_t) == 28U, "draw buffer size drift");
_Static_assert(__builtin_offsetof(lv_draw_buf_t, data_size) == 12U, "data size offset drift");
_Static_assert(__builtin_offsetof(lv_draw_buf_t, data) == 16U, "data offset drift");
_Static_assert(__builtin_offsetof(lv_draw_buf_t, unaligned_data) == 20U, "unaligned offset drift");
_Static_assert(__builtin_offsetof(lv_draw_buf_t, handlers) == 24U, "handler offset drift");
_Static_assert(__builtin_offsetof(lv_draw_buf_handlers_t, buf_free_cb) == 4U, "free callback offset drift");

void open_cfw_draw_buf_lifecycle_probe(lv_draw_buf_t * draw_buf)
{
    lv_draw_buf_destroy(draw_buf);
}
