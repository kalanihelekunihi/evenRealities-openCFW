/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounds-hardened transcription of stateless LVGL operations at commit
 * 344c7c318047b7348e1be8572a9fd4260c251cfa.  Valid LVGL inputs preserve the
 * pinned source behavior.  Null and arithmetically invalid inputs, for which
 * upstream does not define a result, fail closed without allocator, OS, global
 * LVGL state, C library, libm, MMIO, or fixed-address dependencies.
 */

#include "lvgl_ambiq_lvgl_stateless_provider.h"

#include <limits.h>
#include <stdint.h>

#define TRANSFORM_TRIGO_SHIFT 10

static const uint16_t sin0_90_table[] = {
    0, 572, 1144, 1715, 2286, 2856, 3425, 3993, 4560, 5126, 5690, 6252, 6813, 7371, 7927, 8481,
    9032, 9580, 10126, 10668, 11207, 11743, 12275, 12803, 13328, 13848, 14365, 14876, 15384, 15886,
    16384, 16877, 17364, 17847, 18324, 18795, 19261, 19720, 20174, 20622, 21063, 21498, 21926, 22348,
    22763, 23170, 23571, 23965, 24351, 24730, 25102, 25466, 25822, 26170, 26510, 26842, 27166, 27482,
    27789, 28088, 28378, 28660, 28932, 29197, 29452, 29698, 29935, 30163, 30382, 30592, 30792, 30983,
    31164, 31336, 31499, 31651, 31795, 31928, 32052, 32166, 32270, 32365, 32449, 32524, 32588, 32643,
    32688, 32723, 32748, 32763, 32768
};

static int32_t wrap_i64(int64_t value)
{
    return (int32_t)(uint32_t)value;
}

static int32_t arithmetic_shift_i64(int64_t value, unsigned int shift)
{
    uint64_t magnitude;
    uint64_t rounded;

    if(value >= 0) return wrap_i64(value >> shift);
    magnitude = (uint64_t)(-(value + 1)) + 1U;
    rounded = (magnitude + (((uint64_t)1U << shift) - 1U)) >> shift;
    return wrap_i64(-(int64_t)rounded);
}

static int32_t provider_trigo_sin(int32_t angle)
{
    int32_t result;

    angle %= 360;
    if(angle < 0) angle += 360;
    if(angle < 90) result = sin0_90_table[angle];
    else if(angle < 180) result = sin0_90_table[180 - angle];
    else if(angle < 270) result = -(int32_t)sin0_90_table[angle - 180];
    else result = -(int32_t)sin0_90_table[360 - angle];
    return result;
}

static void provider_point_transform(lv_point_t * point, int32_t angle,
                                     int32_t scale_x, int32_t scale_y,
                                     const lv_point_t * pivot)
{
    int32_t angle_low;
    int32_t angle_high;
    int32_t angle_rem;
    int32_t sine;
    int32_t cosine;
    int64_t x;
    int64_t y;

    x = (int64_t)point->x - pivot->x;
    y = (int64_t)point->y - pivot->y;
    if(angle == 0) {
        point->x = wrap_i64(arithmetic_shift_i64(x * scale_x, 8) + pivot->x);
        point->y = wrap_i64(arithmetic_shift_i64(y * scale_y, 8) + pivot->y);
        return;
    }

    angle %= 3600;
    if(angle < 0) angle += 3600;
    angle_low = angle / 10;
    angle_high = angle_low + 1;
    angle_rem = angle - angle_low * 10;
    sine = (provider_trigo_sin(angle_low) * (10 - angle_rem) +
            provider_trigo_sin(angle_high) * angle_rem) / 10;
    cosine = (provider_trigo_sin(angle_low + 90) * (10 - angle_rem) +
              provider_trigo_sin(angle_high + 90) * angle_rem) / 10;
    sine >>= LV_TRIGO_SHIFT - TRANSFORM_TRIGO_SHIFT;
    cosine >>= LV_TRIGO_SHIFT - TRANSFORM_TRIGO_SHIFT;

    x *= scale_x;
    y *= scale_y;
    point->x = wrap_i64(
        arithmetic_shift_i64((int64_t)cosine * x - (int64_t)sine * y,
                             TRANSFORM_TRIGO_SHIFT + 8) + pivot->x
    );
    point->y = wrap_i64(
        arithmetic_shift_i64((int64_t)sine * x + (int64_t)cosine * y,
                             TRANSFORM_TRIGO_SHIFT + 8) + pivot->y
    );
}

void lv_array_init_from_buf(lv_array_t * array, void * buffer, uint32_t capacity,
                            uint32_t element_size)
{
    if(array == NULL) return;
    array->size = 0;
    array->capacity = buffer == NULL ? 0 : capacity;
    array->element_size = element_size;
    array->data = buffer;
    array->inner_alloc = false;
}

void * lv_array_at(const lv_array_t * array, uint32_t index)
{
    size_t offset;

    if(array == NULL || index >= array->size || array->data == NULL) return NULL;
    if(array->element_size != 0 && index > SIZE_MAX / array->element_size) return NULL;
    offset = (size_t)index * array->element_size;
    return array->data + offset;
}

void lv_draw_buf_invalidate_cache(const lv_draw_buf_t * draw_buf,
                                  const lv_area_t * area)
{
    lv_area_t full;

    if(draw_buf == NULL || draw_buf->handlers == NULL ||
       draw_buf->handlers->invalidate_cache_cb == NULL) return;
    if(area == NULL) {
        full.x1 = 0;
        full.y1 = 0;
        full.x2 = draw_buf->header.w == 0 ? -1 : (int32_t)(draw_buf->header.w - 1U);
        full.y2 = draw_buf->header.h == 0 ? -1 : (int32_t)(draw_buf->header.h - 1U);
        area = &full;
    }
    draw_buf->handlers->invalidate_cache_cb(draw_buf, area);
}

void lv_draw_buf_flush_cache(const lv_draw_buf_t * draw_buf, const lv_area_t * area)
{
    lv_area_t full;

    if(draw_buf == NULL || draw_buf->handlers == NULL ||
       draw_buf->handlers->flush_cache_cb == NULL) return;
    if(area == NULL) {
        full.x1 = 0;
        full.y1 = 0;
        full.x2 = draw_buf->header.w == 0 ? -1 : (int32_t)(draw_buf->header.w - 1U);
        full.y2 = draw_buf->header.h == 0 ? -1 : (int32_t)(draw_buf->header.h - 1U);
        area = &full;
    }
    draw_buf->handlers->flush_cache_cb(draw_buf, area);
}

void lv_draw_image_dsc_init(lv_draw_image_dsc_t * descriptor)
{
    if(descriptor == NULL) return;
    lv_memset(descriptor, 0, sizeof(*descriptor));
    descriptor->opa = LV_OPA_COVER;
    descriptor->scale_x = LV_SCALE_NONE;
    descriptor->scale_y = LV_SCALE_NONE;
    descriptor->antialias = LV_COLOR_DEPTH > 8 ? 1U : 0U;
    descriptor->image_area.x2 = LV_COORD_MIN;
    descriptor->base.dsc_size = sizeof(*descriptor);
}

const void * lv_font_get_glyph_bitmap(lv_font_glyph_dsc_t * glyph,
                                      lv_draw_buf_t * draw_buf)
{
    const lv_font_t * font;

    if(glyph == NULL) return NULL;
    font = glyph->resolved_font;
    if(font == NULL || font->get_glyph_bitmap == NULL) return NULL;
    return font->get_glyph_bitmap(glyph, draw_buf);
}

uint32_t lv_freetype_outline_get_scale(const lv_font_t * font)
{
    const lv_freetype_font_dsc_t * descriptor;

    if(font == NULL || font->dsc == NULL) return 0;
    descriptor = font->dsc;
    if(!LV_FREETYPE_FONT_DSC_HAS_MAGIC_NUM(descriptor) ||
       descriptor->cache_node == NULL || descriptor->cache_node->ref_size == 0) return 0;
    return (descriptor->size << 6) / descriptor->cache_node->ref_size;
}

bool lv_freetype_is_outline_font(const lv_font_t * font)
{
    const lv_freetype_font_dsc_t * descriptor;

    if(font == NULL || font->dsc == NULL) return false;
    descriptor = font->dsc;
    if(!LV_FREETYPE_FONT_DSC_HAS_MAGIC_NUM(descriptor)) return false;
    return descriptor->render_mode == LV_FREETYPE_FONT_RENDER_MODE_OUTLINE;
}

void lv_image_buf_get_transformed_area(lv_area_t * result, int32_t width,
                                       int32_t height, int32_t angle,
                                       uint16_t scale_x, uint16_t scale_y,
                                       const lv_point_t * pivot)
{
    lv_point_t points[4];
    int32_t min_x;
    int32_t max_x;
    int32_t min_y;
    int32_t max_y;
    unsigned int index;

    if(result == NULL || pivot == NULL) return;
    if(width < 0 || height < 0) {
        result->x1 = 0;
        result->y1 = 0;
        result->x2 = -1;
        result->y2 = -1;
        return;
    }
    if(angle == 0 && scale_x == LV_SCALE_NONE && scale_y == LV_SCALE_NONE) {
        result->x1 = 0;
        result->y1 = 0;
        result->x2 = wrap_i64((int64_t)width - 1);
        result->y2 = wrap_i64((int64_t)height - 1);
        return;
    }

    points[0].x = 0;
    points[0].y = 0;
    points[1].x = width;
    points[1].y = 0;
    points[2].x = 0;
    points[2].y = height;
    points[3].x = width;
    points[3].y = height;
    for(index = 0; index < 4; ++index) {
        provider_point_transform(&points[index], angle, scale_x, scale_y, pivot);
    }
    min_x = max_x = points[0].x;
    min_y = max_y = points[0].y;
    for(index = 1; index < 4; ++index) {
        if(points[index].x < min_x) min_x = points[index].x;
        if(points[index].x > max_x) max_x = points[index].x;
        if(points[index].y < min_y) min_y = points[index].y;
        if(points[index].y > max_y) max_y = points[index].y;
    }
    result->x1 = min_x;
    result->x2 = wrap_i64((int64_t)max_x - 1);
    result->y1 = min_y;
    result->y2 = wrap_i64((int64_t)max_y - 1);
}

void * lv_memcpy(void * destination, const void * source, size_t length)
{
    volatile uint8_t * output = destination;
    const uint8_t * input = source;
    void * original = destination;

    if(length == 0) return original;
    if(output == NULL || input == NULL) return NULL;
    while(length-- != 0) *output++ = *input++;
    return original;
}

void lv_memset(void * destination, uint8_t value, size_t length)
{
    volatile uint8_t * output = destination;

    if(output == NULL) return;
    while(length-- != 0) *output++ = value;
}
