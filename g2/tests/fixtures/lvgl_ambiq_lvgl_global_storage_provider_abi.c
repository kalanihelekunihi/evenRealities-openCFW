/* SPDX-License-Identifier: MIT */
#include <stddef.h>

#include "lvgl_ambiq_lvgl_global_storage_provider.h"

_Static_assert(sizeof(lv_global_t) == 0x1ECU, "lv_global_t ABI");
_Static_assert(offsetof(lv_global_t, draw_buf_handlers) == 0xC8U,
               "draw_buf_handlers ABI");
_Static_assert(offsetof(lv_global_t, font_draw_buf_handlers) == 0xE8U,
               "font_draw_buf_handlers ABI");
_Static_assert(offsetof(lv_global_t, image_cache_draw_buf_handlers) == 0x108U,
               "image_cache_draw_buf_handlers ABI");

lv_global_t * open_cfw_lvgl_global_storage_probe(void)
{
    return &lv_global;
}
