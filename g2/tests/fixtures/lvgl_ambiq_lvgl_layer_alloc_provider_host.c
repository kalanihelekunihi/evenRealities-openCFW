/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_layer_alloc_provider.h"
#include "src/core/lv_global.h"
#include "src/draw/lv_draw_buf_private.h"

#include <assert.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

lv_global_t lv_global;

static lv_draw_buf_t draw_buf;
static uint8_t storage[512];
static unsigned create_calls;
static unsigned destroy_calls;
static unsigned flush_calls;
static unsigned log_calls;
static int fail_create;
static int malformed_create;

int32_t lv_area_get_width(const lv_area_t * area)
{
    return area->x2 - area->x1 + 1;
}

int32_t lv_area_get_height(const lv_area_t * area)
{
    return area->y2 - area->y1 + 1;
}

void lv_memset(void * destination, uint8_t value, size_t length)
{
    (void)memset(destination, value, length);
}

static uint32_t width_to_stride(uint32_t width, lv_color_format_t format)
{
    (void)format;
    return width * 4U;
}

lv_draw_buf_t * lv_draw_buf_create(uint32_t width, uint32_t height,
                                   lv_color_format_t format, uint32_t stride)
{
    create_calls++;
    if(fail_create) return NULL;
    memset(&draw_buf, 0, sizeof(draw_buf));
    memset(storage, 0xA5, sizeof(storage));
    draw_buf.header.w = width;
    draw_buf.header.h = height;
    draw_buf.header.cf = format;
    draw_buf.header.stride = stride != 0U ? stride : width_to_stride(width, format);
    draw_buf.data = storage;
    draw_buf.data_size = malformed_create ? 1U : sizeof(storage);
    return &draw_buf;
}

void lv_draw_buf_destroy(lv_draw_buf_t * buffer)
{
    assert(buffer == &draw_buf);
    destroy_calls++;
}

void lv_draw_buf_flush_cache(const lv_draw_buf_t * buffer, const lv_area_t * area)
{
    assert(buffer == &draw_buf);
    assert(area == NULL);
    flush_calls++;
}

void lv_log_add(lv_log_level_t level, const char * file, int line,
                const char * function, const char * format, ...)
{
    (void)file;
    (void)line;
    (void)function;
    assert(level == LV_LOG_LEVEL_WARN);
    assert(strcmp(format, "Allocating layer buffer failed. Try later") == 0);
    log_calls++;
}

static void reset_layer(lv_layer_t * layer, lv_color_format_t format,
                        int32_t width, int32_t height)
{
    memset(layer, 0, sizeof(*layer));
    layer->color_format = format;
    layer->buf_area.x1 = 0;
    layer->buf_area.y1 = 0;
    layer->buf_area.x2 = width - 1;
    layer->buf_area.y2 = height - 1;
}

int main(void)
{
    lv_layer_t layer;
    void * result;

    memset(&lv_global, 0, sizeof(lv_global));
    assert(lv_draw_layer_alloc_buf(NULL) == NULL);

    reset_layer(&layer, LV_COLOR_FORMAT_ARGB8888, 0, 4);
    assert(lv_draw_layer_alloc_buf(&layer) == NULL);
    reset_layer(&layer, LV_COLOR_FORMAT_ARGB8888, 4, 0);
    assert(lv_draw_layer_alloc_buf(&layer) == NULL);
    assert(create_calls == 0U);

    reset_layer(&layer, LV_COLOR_FORMAT_ARGB8888, 4, 4);
    assert(lv_draw_layer_alloc_buf(&layer) == NULL);
    assert(create_calls == 0U);
    lv_global.draw_buf_handlers.width_to_stride_cb = width_to_stride;

    fail_create = 1;
    assert(lv_draw_layer_alloc_buf(&layer) == NULL);
    assert(create_calls == 1U && log_calls == 1U);
    fail_create = 0;

    malformed_create = 1;
    assert(lv_draw_layer_alloc_buf(&layer) == NULL);
    assert(destroy_calls == 1U);
    assert(lv_global.draw_info.used_memory_for_layers == 0U);
    malformed_create = 0;

    result = lv_draw_layer_alloc_buf(&layer);
    assert(result == storage);
    assert(layer.draw_buf == &draw_buf);
    assert(lv_global.draw_info.used_memory_for_layers == 64U);
    assert(flush_calls == 1U);
    for(unsigned i = 0; i < 64U; i++) assert(storage[i] == 0U);
    assert(lv_draw_layer_alloc_buf(&layer) == storage);
    assert(create_calls == 3U);

    reset_layer(&layer, LV_COLOR_FORMAT_RGB565, 4, 4);
    result = lv_draw_layer_alloc_buf(&layer);
    assert(result == storage);
    assert(flush_calls == 1U);
    assert(storage[0] == 0xA5U);

    lv_global.draw_info.used_memory_for_layers = UINT32_MAX - 1U;
    reset_layer(&layer, LV_COLOR_FORMAT_RGB565, 4, 4);
    assert(lv_draw_layer_alloc_buf(&layer) == NULL);
    assert(destroy_calls == 2U);
    assert(layer.draw_buf == NULL);
    return 0;
}
