/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Isolated definition of LVGL's default global object from authenticated
 * commit 344c7c318047b7348e1be8572a9fd4260c251cfa.  This translation unit owns
 * storage only.  It deliberately does not initialize handler tables, create
 * decoder/cache state, or select an OS/scheduler policy.
 */

#include <stddef.h>
#include <stdint.h>

#include "lvgl_ambiq_lvgl_global_storage_provider.h"

#if LV_ENABLE_GLOBAL_CUSTOM != 0
#error "G2 uses LVGL's default lv_global object ABI"
#endif

_Static_assert(sizeof(void *) == 4U, "G2 lv_global requires 32-bit pointers");
_Static_assert(sizeof(lv_global_t) == 0x1ECU, "G2 lv_global size changed");
_Static_assert(offsetof(lv_global_t, draw_buf_handlers) == 0xC8U,
               "G2 default draw-buffer handler offset changed");
_Static_assert(offsetof(lv_global_t, font_draw_buf_handlers) == 0xE8U,
               "G2 font draw-buffer handler offset changed");
_Static_assert(offsetof(lv_global_t, image_cache_draw_buf_handlers) == 0x108U,
               "G2 image-cache draw-buffer handler offset changed");
_Static_assert(offsetof(lv_global_t, user_data) == 0x1E8U,
               "G2 lv_global terminal field offset changed");

lv_global_t lv_global;
