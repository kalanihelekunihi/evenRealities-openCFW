/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_decoder_support_provider.h"
#include "src/core/lv_global.h"
#include "src/misc/cache/lv_cache_private.h"

#include <assert.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

lv_global_t lv_global;

void * lv_malloc(size_t size)
{
    return malloc(size);
}

void * lv_memcpy(void * destination, const void * source, size_t length)
{
    return memcpy(destination, source, length);
}

int main(void)
{
    lv_cache_t image_cache;
    lv_cache_t header_cache;
    struct node {
        uint32_t value;
        struct node * previous;
        struct node * next;
    } first, second;
    lv_ll_t list;
    const uint8_t variable[] = {0x00U};
    const uint8_t symbol[] = {0x80U};
    char * duplicate;

    memset(&lv_global, 0, sizeof(lv_global));
    memset(&image_cache, 0, sizeof(image_cache));
    memset(&header_cache, 0, sizeof(header_cache));
    assert(lv_image_src_get_type(NULL) == LV_IMAGE_SRC_UNKNOWN);
    assert(lv_image_src_get_type("asset.bin") == LV_IMAGE_SRC_FILE);
    assert(lv_image_src_get_type(variable) == LV_IMAGE_SRC_VARIABLE);
    assert(lv_image_src_get_type(symbol) == LV_IMAGE_SRC_SYMBOL);

    assert(!lv_image_cache_is_enabled());
    assert(!lv_image_header_cache_is_enabled());
    lv_global.img_cache = &image_cache;
    lv_global.img_header_cache = &header_cache;
    image_cache.max_size = 1U;
    assert(lv_image_cache_is_enabled());
    assert(!lv_image_header_cache_is_enabled());
    header_cache.max_size = 2U;
    assert(lv_image_header_cache_is_enabled());

    memset(&first, 0, sizeof(first));
    memset(&second, 0, sizeof(second));
    first.value = 1U;
    second.value = 2U;
    first.next = &second;
    list.n_size = offsetof(struct node, previous);
    list.head = (lv_ll_node_t *)&first;
    list.tail = (lv_ll_node_t *)&second;
    assert(lv_ll_get_head(NULL) == NULL);
    assert(lv_ll_get_head(&list) == &first);
    assert(lv_ll_get_next(&list, &first) == &second);
    assert(lv_ll_get_next(NULL, &first) == NULL);
    assert(lv_ll_get_next(&list, NULL) == NULL);

    assert(lv_strdup(NULL) == NULL);
    duplicate = lv_strdup("decoder");
    assert(duplicate != NULL);
    assert(strcmp(duplicate, "decoder") == 0);
    free(duplicate);
    return 0;
}
