/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Exact small support leaves used by lv_image_decoder_open/close at LVGL
 * commit 344c7c318047b7348e1be8572a9fd4260c251cfa. Bounds checks affect only
 * invalid inputs which upstream treats as caller-contract violations.
 */

#include <stddef.h>
#include <stdint.h>

#include "lvgl_ambiq_lvgl_decoder_support_provider.h"
#include "src/core/lv_global.h"
#include "src/misc/cache/lv_cache_private.h"
#include "src/stdlib/lv_mem.h"

lv_image_src_t lv_image_src_get_type(const void * source)
{
    const uint8_t * byte = source;
    if(byte == NULL) return LV_IMAGE_SRC_UNKNOWN;
    if(byte[0] >= 0x20U && byte[0] <= 0x7FU) return LV_IMAGE_SRC_FILE;
    if(byte[0] >= 0x80U) return LV_IMAGE_SRC_SYMBOL;
    return LV_IMAGE_SRC_VARIABLE;
}

bool lv_image_cache_is_enabled(void)
{
    const lv_cache_t * cache = LV_GLOBAL_DEFAULT()->img_cache;
    return cache != NULL && cache->max_size > 0U;
}

bool lv_image_header_cache_is_enabled(void)
{
    const lv_cache_t * cache = LV_GLOBAL_DEFAULT()->img_header_cache;
    return cache != NULL && cache->max_size > 0U;
}

void * lv_ll_get_head(const lv_ll_t * list)
{
    return list != NULL ? list->head : NULL;
}

void * lv_ll_get_next(const lv_ll_t * list, const void * node)
{
    const uint8_t * bytes = node;
    lv_ll_node_t * const * next;

    if(list == NULL || bytes == NULL) return NULL;
    next = (lv_ll_node_t * const *)(const void *)(
        bytes + list->n_size + sizeof(lv_ll_node_t *));
    return *next;
}

char * lv_strdup(const char * source)
{
    const char * cursor;
    size_t length;
    char * duplicate;

    if(source == NULL) return NULL;
    cursor = source;
    while(*cursor != '\0') cursor++;
    length = (size_t)(cursor - source) + 1U;
    duplicate = lv_malloc(length);
    if(duplicate == NULL) return NULL;
    lv_memcpy(duplicate, source, length);
    return duplicate;
}
