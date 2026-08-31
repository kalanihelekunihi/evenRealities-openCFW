/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_stateless_provider.h"

#include <assert.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>

static unsigned int flush_calls;
static unsigned int invalidate_calls;
static lv_area_t cache_area;
static const lv_draw_buf_t * cache_buffer;
static lv_font_glyph_dsc_t * bitmap_glyph;
static lv_draw_buf_t * bitmap_buffer;
static const uint8_t bitmap_marker = 0xA5;

static void flush_cb(const lv_draw_buf_t * draw_buf, const lv_area_t * area)
{
    ++flush_calls;
    cache_buffer = draw_buf;
    cache_area = *area;
}

static void invalidate_cb(const lv_draw_buf_t * draw_buf, const lv_area_t * area)
{
    ++invalidate_calls;
    cache_buffer = draw_buf;
    cache_area = *area;
}

static const void * bitmap_cb(lv_font_glyph_dsc_t * glyph, lv_draw_buf_t * draw_buf)
{
    bitmap_glyph = glyph;
    bitmap_buffer = draw_buf;
    return &bitmap_marker;
}

static void test_array_and_memory(void)
{
    uint32_t words[3] = {0x11223344U, 0x55667788U, 0x99AABBCCU};
    uint8_t source[19];
    uint8_t destination[21];
    lv_array_t array;
    unsigned int index;

    lv_array_init_from_buf(&array, words, 3, sizeof(words[0]));
    assert(array.size == 0 && array.capacity == 3 && !array.inner_alloc);
    array.size = 3;
    assert(lv_array_at(&array, 0) == &words[0]);
    assert(lv_array_at(&array, 2) == &words[2]);
    assert(lv_array_at(&array, 3) == NULL);
    assert(lv_array_at(NULL, 0) == NULL);
    lv_array_init_from_buf(&array, NULL, UINT32_MAX, UINT32_MAX);
    assert(array.data == NULL && array.capacity == 0 && array.size == 0);
    lv_array_init_from_buf(NULL, words, 3, sizeof(words[0]));

    for(index = 0; index < sizeof(source); ++index) source[index] = (uint8_t)(index * 7U);
    lv_memset(destination, 0x5A, sizeof(destination));
    assert(destination[0] == 0x5A && destination[20] == 0x5A);
    assert(lv_memcpy(destination + 1, source, sizeof(source)) == destination + 1);
    for(index = 0; index < sizeof(source); ++index) assert(destination[index + 1] == source[index]);
    assert(lv_memcpy(NULL, NULL, 0) == NULL);
    assert(lv_memcpy(NULL, source, 1) == NULL);
    assert(lv_memcpy(destination, NULL, 1) == NULL);
    lv_memset(NULL, 0xFF, SIZE_MAX);
}

static void test_cache_callbacks(void)
{
    lv_draw_buf_handlers_t handlers = {0};
    lv_draw_buf_t draw_buf = {0};
    lv_area_t explicit_area = {1, 2, 3, 4};

    handlers.flush_cache_cb = flush_cb;
    handlers.invalidate_cache_cb = invalidate_cb;
    draw_buf.handlers = &handlers;
    draw_buf.header.w = 7;
    draw_buf.header.h = 5;

    lv_draw_buf_flush_cache(&draw_buf, NULL);
    assert(flush_calls == 1 && cache_buffer == &draw_buf);
    assert(cache_area.x1 == 0 && cache_area.y1 == 0 && cache_area.x2 == 6 && cache_area.y2 == 4);
    lv_draw_buf_invalidate_cache(&draw_buf, &explicit_area);
    assert(invalidate_calls == 1 && cache_buffer == &draw_buf);
    assert(cache_area.x1 == 1 && cache_area.y1 == 2 && cache_area.x2 == 3 && cache_area.y2 == 4);

    lv_draw_buf_flush_cache(NULL, NULL);
    lv_draw_buf_invalidate_cache(NULL, NULL);
    draw_buf.handlers = NULL;
    lv_draw_buf_flush_cache(&draw_buf, NULL);
    lv_draw_buf_invalidate_cache(&draw_buf, NULL);
    assert(flush_calls == 1 && invalidate_calls == 1);
}

static void test_image_and_font_descriptors(void)
{
    lv_draw_image_dsc_t image;
    lv_font_t font = {0};
    lv_font_glyph_dsc_t glyph = {0};
    lv_draw_buf_t draw_buf = {0};
    lv_freetype_font_dsc_t freetype = {0};
    lv_freetype_cache_node_t cache_node = {0};

    lv_memset(&image, 0xA5, sizeof(image));
    lv_draw_image_dsc_init(&image);
    assert(image.recolor.red == 0 && image.recolor.green == 0 && image.recolor.blue == 0);
    assert(image.opa == LV_OPA_COVER);
    assert(image.scale_x == LV_SCALE_NONE && image.scale_y == LV_SCALE_NONE);
    assert(image.antialias == 0);
    assert(image.image_area.x2 == LV_COORD_MIN);
    assert(image.base.dsc_size == sizeof(image));
    lv_draw_image_dsc_init(NULL);

    font.get_glyph_bitmap = bitmap_cb;
    glyph.resolved_font = &font;
    assert(lv_font_get_glyph_bitmap(&glyph, &draw_buf) == &bitmap_marker);
    assert(bitmap_glyph == &glyph && bitmap_buffer == &draw_buf);
    assert(lv_font_get_glyph_bitmap(NULL, &draw_buf) == NULL);
    glyph.resolved_font = NULL;
    assert(lv_font_get_glyph_bitmap(&glyph, &draw_buf) == NULL);

    freetype.magic_num = LV_FREETYPE_FONT_DSC_MAGIC_NUM;
    freetype.size = 12;
    freetype.render_mode = LV_FREETYPE_FONT_RENDER_MODE_OUTLINE;
    freetype.cache_node = &cache_node;
    cache_node.ref_size = 24;
    font.dsc = &freetype;
    assert(lv_freetype_is_outline_font(&font));
    assert(lv_freetype_outline_get_scale(&font) == 32);
    cache_node.ref_size = 0;
    assert(lv_freetype_outline_get_scale(&font) == 0);
    freetype.magic_num = 0;
    assert(!lv_freetype_is_outline_font(&font));
    assert(lv_freetype_outline_get_scale(&font) == 0);
    assert(!lv_freetype_is_outline_font(NULL));
    assert(lv_freetype_outline_get_scale(NULL) == 0);
}

static void test_transformed_area(void)
{
    const lv_point_t pivot = {0, 0};
    lv_area_t area = {7, 7, 7, 7};

    lv_image_buf_get_transformed_area(&area, 10, 20, 0, 256, 256, &pivot);
    assert(area.x1 == 0 && area.y1 == 0 && area.x2 == 9 && area.y2 == 19);
    lv_image_buf_get_transformed_area(&area, 10, 20, 0, 512, 512, &pivot);
    assert(area.x1 == 0 && area.y1 == 0 && area.x2 == 19 && area.y2 == 39);
    lv_image_buf_get_transformed_area(&area, 10, 20, 900, 256, 256, &pivot);
    assert(area.x1 == -20 && area.y1 == 0 && area.x2 == -1 && area.y2 == 9);

    lv_image_buf_get_transformed_area(&area, -1, INT32_MAX, INT32_MAX,
                                      UINT16_MAX, UINT16_MAX, &pivot);
    assert(area.x1 == 0 && area.y1 == 0 && area.x2 == -1 && area.y2 == -1);
    area.x1 = 123;
    lv_image_buf_get_transformed_area(NULL, 1, 1, 0, 256, 256, &pivot);
    lv_image_buf_get_transformed_area(&area, 1, 1, 0, 256, 256, NULL);
    assert(area.x1 == 123);
}

int main(void)
{
    test_array_and_memory();
    test_cache_callbacks();
    test_image_and_font_descriptors();
    test_transformed_area();
    return 0;
}
