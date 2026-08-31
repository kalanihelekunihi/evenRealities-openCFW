/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_stateless_provider.h"

_Static_assert(sizeof(void *) == 4, "G2 pointer ABI changed");
_Static_assert(sizeof(lv_array_t) == 20, "lv_array_t ABI changed");
_Static_assert(sizeof(lv_draw_buf_t) == 28, "lv_draw_buf_t ABI changed");
_Static_assert(sizeof(lv_draw_buf_handlers_t) == 32, "G2 draw-buffer handler ABI changed");

void open_cfw_lvgl_stateless_provider_abi_probe(void)
{
    void (*array_init)(lv_array_t *, void *, uint32_t, uint32_t) = lv_array_init_from_buf;
    void * (*array_at)(const lv_array_t *, uint32_t) = lv_array_at;
    void (*flush)(const lv_draw_buf_t *, const lv_area_t *) = lv_draw_buf_flush_cache;
    void (*invalidate)(const lv_draw_buf_t *, const lv_area_t *) = lv_draw_buf_invalidate_cache;
    void (*image_init)(lv_draw_image_dsc_t *) = lv_draw_image_dsc_init;
    const void * (*glyph_bitmap)(lv_font_glyph_dsc_t *, lv_draw_buf_t *) = lv_font_get_glyph_bitmap;
    uint32_t (*outline_scale)(const lv_font_t *) = lv_freetype_outline_get_scale;
    bool (*is_outline)(const lv_font_t *) = lv_freetype_is_outline_font;
    void (*transform)(lv_area_t *, int32_t, int32_t, int32_t, uint16_t, uint16_t,
                      const lv_point_t *) = lv_image_buf_get_transformed_area;
    void * (*memory_copy)(void *, const void *, size_t) = lv_memcpy;
    void (*memory_set)(void *, uint8_t, size_t) = lv_memset;

    (void)array_init;
    (void)array_at;
    (void)flush;
    (void)invalidate;
    (void)image_init;
    (void)glyph_bitmap;
    (void)outline_scale;
    (void)is_outline;
    (void)transform;
    (void)memory_copy;
    (void)memory_set;
}
