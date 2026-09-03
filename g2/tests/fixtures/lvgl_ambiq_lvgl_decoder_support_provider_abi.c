/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_decoder_support_provider.h"

void open_cfw_lvgl_decoder_support_probe(const void * source, const lv_ll_t * list,
                                          const void * node)
{
    (void)lv_image_src_get_type(source);
    (void)lv_image_cache_is_enabled();
    (void)lv_image_header_cache_is_enabled();
    (void)lv_ll_get_head(list);
    (void)lv_ll_get_next(list, node);
    (void)lv_strdup((const char *)source);
}
