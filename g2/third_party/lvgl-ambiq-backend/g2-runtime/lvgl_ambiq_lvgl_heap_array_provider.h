/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_HEAP_ARRAY_PROVIDER_H
#define OPEN_CFW_LVGL_AMBIQ_HEAP_ARRAY_PROVIDER_H

#include "lvgl.h"

#ifdef __cplusplus
extern "C" {
#endif

/* The declarations are repeated here so the isolated provider ABI is explicit. */
void * lv_malloc(size_t size);
void * lv_malloc_zeroed(size_t size);
void lv_free(void * data);
void lv_array_deinit(lv_array_t * array);
lv_result_t lv_array_push_back(lv_array_t * array, const void * element);

#ifdef __cplusplus
}
#endif

#endif
