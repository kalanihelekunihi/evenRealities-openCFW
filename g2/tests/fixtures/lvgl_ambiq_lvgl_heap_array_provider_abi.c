/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_heap_array_provider.h"

_Static_assert(sizeof(lv_array_t) == 20U, "lv_array_t size drift");
_Static_assert(__builtin_offsetof(lv_array_t, data) == 0U, "data offset drift");
_Static_assert(__builtin_offsetof(lv_array_t, size) == 4U, "size offset drift");
_Static_assert(__builtin_offsetof(lv_array_t, capacity) == 8U, "capacity offset drift");
_Static_assert(__builtin_offsetof(lv_array_t, element_size) == 12U, "element size offset drift");
_Static_assert(__builtin_offsetof(lv_array_t, inner_alloc) == 16U, "ownership offset drift");

void * open_cfw_heap_array_probe_malloc(size_t size) { return lv_malloc(size); }
void * open_cfw_heap_array_probe_malloc_zeroed(size_t size) { return lv_malloc_zeroed(size); }
void open_cfw_heap_array_probe_free(void * pointer) { lv_free(pointer); }
void open_cfw_heap_array_probe_deinit(lv_array_t * array) { lv_array_deinit(array); }
lv_result_t open_cfw_heap_array_probe_push(lv_array_t * array, const void * element)
{
    return lv_array_push_back(array, element);
}
