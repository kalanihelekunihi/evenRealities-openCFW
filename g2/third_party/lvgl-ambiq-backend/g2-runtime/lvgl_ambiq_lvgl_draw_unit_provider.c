/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounded transcription of lv_draw_create_unit from authenticated LVGL
 * commit 344c7c318047b7348e1be8572a9fd4260c251cfa.  The valid-input path keeps
 * LVGL's allocation, head insertion, monotonically increasing ID, and zeroed
 * extension semantics.  Invalid allocation extents, allocator failure, and an
 * ID which cannot be represented by lv_draw_unit_t::idx fail before mutation.
 */

#include <limits.h>
#include <stddef.h>
#include <stdint.h>

#include "lvgl_ambiq_lvgl_draw_unit_provider.h"
#include "src/core/lv_global.h"
#include "src/stdlib/lv_mem.h"

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(lv_draw_unit_t) == 28U, "G2 draw-unit ABI size changed");
_Static_assert(offsetof(lv_draw_unit_t, next) == 0U, "G2 draw-unit next offset changed");
_Static_assert(offsetof(lv_draw_unit_t, idx) == 8U, "G2 draw-unit idx offset changed");
#endif

void * lv_draw_create_unit(size_t size)
{
    lv_draw_global_info_t * draw_info = &LV_GLOBAL_DEFAULT()->draw_info;
    lv_draw_unit_t * new_unit;

    if(size < sizeof(*new_unit) || draw_info->unit_cnt >= (uint32_t)INT32_MAX) {
        return NULL;
    }

    new_unit = lv_malloc_zeroed(size);
    if(new_unit == NULL) return NULL;

    new_unit->next = draw_info->unit_head;
    draw_info->unit_head = new_unit;
    draw_info->unit_cnt++;
    new_unit->idx = (int32_t)draw_info->unit_cnt;
    return new_unit;
}
