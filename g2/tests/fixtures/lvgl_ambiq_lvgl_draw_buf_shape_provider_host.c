/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "lvgl_ambiq_lvgl_draw_buf_shape_provider.h"

static lv_draw_buf_handlers_t handlers;
static const lv_draw_buf_handlers_t * selected_handlers;
static unsigned int descriptor_allocations;
static unsigned int descriptor_frees;
static unsigned int buffer_allocations;
static unsigned int buffer_frees;
static bool fail_descriptor;
static bool fail_buffer;
static bool fail_align;

const lv_draw_buf_handlers_t * open_cfw_test_draw_buf_handlers(void)
{
    return selected_handlers;
}

void * lv_malloc_zeroed(size_t size)
{
    if(fail_descriptor) return NULL;
    descriptor_allocations++;
    return calloc(1U, size);
}

void lv_free(void * data)
{
    if(data != NULL) descriptor_frees++;
    free(data);
}

static void * buffer_malloc(size_t size, lv_color_format_t cf)
{
    (void)cf;
    if(fail_buffer) return NULL;
    buffer_allocations++;
    return malloc(size);
}

static void buffer_free(void * data)
{
    if(data != NULL) buffer_frees++;
    free(data);
}

static void * buffer_align(void * data, lv_color_format_t cf)
{
    (void)cf;
    return fail_align ? NULL : data;
}

static uint32_t width_to_stride(uint32_t width, lv_color_format_t cf)
{
    (void)cf;
    return (width + 3U) & ~3U;
}

static void reset_state(void)
{
    memset(&handlers, 0, sizeof(handlers));
    handlers.buf_malloc_cb = buffer_malloc;
    handlers.buf_free_cb = buffer_free;
    handlers.align_pointer_cb = buffer_align;
    handlers.width_to_stride_cb = width_to_stride;
    selected_handlers = &handlers;
    descriptor_allocations = 0U;
    descriptor_frees = 0U;
    buffer_allocations = 0U;
    buffer_frees = 0U;
    fail_descriptor = false;
    fail_buffer = false;
    fail_align = false;
}

int main(void)
{
    lv_draw_buf_t * draw_buf;
    lv_draw_buf_t snapshot;

    reset_state();
    selected_handlers = NULL;
    assert(lv_draw_buf_create(4U, 4U, LV_COLOR_FORMAT_A8, 0U) == NULL);
    assert(descriptor_allocations == 0U);

    reset_state();
    handlers.width_to_stride_cb = NULL;
    assert(lv_draw_buf_create(4U, 4U, LV_COLOR_FORMAT_A8, 0U) == NULL);
    assert(lv_draw_buf_create(UINT16_MAX + 1U, 1U, LV_COLOR_FORMAT_A8, 4U) == NULL);
    assert(lv_draw_buf_create(1U, UINT16_MAX + 1U, LV_COLOR_FORMAT_A8, 4U) == NULL);
    assert(lv_draw_buf_create(1U, 1U, LV_COLOR_FORMAT_A8, UINT16_MAX + 1U) == NULL);
    assert(descriptor_allocations == 4U && descriptor_frees == 4U);

    reset_state();
    fail_descriptor = true;
    assert(lv_draw_buf_create(4U, 4U, LV_COLOR_FORMAT_A8, 0U) == NULL);
    fail_descriptor = false;
    fail_buffer = true;
    assert(lv_draw_buf_create(4U, 4U, LV_COLOR_FORMAT_A8, 0U) == NULL);
    assert(descriptor_allocations == 1U && descriptor_frees == 1U);
    fail_buffer = false;
    fail_align = true;
    assert(lv_draw_buf_create(4U, 4U, LV_COLOR_FORMAT_A8, 0U) == NULL);
    assert(buffer_allocations == 1U && buffer_frees == 1U);
    assert(descriptor_allocations == 2U && descriptor_frees == 2U);

    reset_state();
    draw_buf = lv_draw_buf_create(7U, 5U, LV_COLOR_FORMAT_A8, 0U);
    assert(draw_buf != NULL);
    assert(draw_buf->header.w == 7U && draw_buf->header.h == 5U);
    assert(draw_buf->header.stride == 8U);
    assert(draw_buf->header.cf == LV_COLOR_FORMAT_A8);
    assert(draw_buf->header.magic == LV_IMAGE_HEADER_MAGIC);
    assert((draw_buf->header.flags & LV_IMAGE_FLAGS_ALLOCATED) != 0U);
    assert((draw_buf->header.flags & LV_IMAGE_FLAGS_MODIFIABLE) != 0U);
    assert(draw_buf->data_size == 40U && draw_buf->data == draw_buf->unaligned_data);
    assert(draw_buf->handlers == &handlers);

    assert(lv_draw_buf_reshape(draw_buf, LV_COLOR_FORMAT_UNKNOWN, 4U, 5U, 0U) == draw_buf);
    assert(draw_buf->header.cf == LV_COLOR_FORMAT_A8);
    assert(draw_buf->header.w == 4U && draw_buf->header.stride == 4U);
    snapshot = *draw_buf;
    assert(lv_draw_buf_reshape(draw_buf, LV_COLOR_FORMAT_A8, 20U, 20U, 20U) == NULL);
    assert(memcmp(&snapshot, draw_buf, sizeof(snapshot)) == 0);
    assert(lv_draw_buf_reshape(draw_buf, LV_COLOR_FORMAT_A8, UINT16_MAX + 1U, 1U, 4U) == NULL);
    assert(memcmp(&snapshot, draw_buf, sizeof(snapshot)) == 0);

    handlers.width_to_stride_cb = NULL;
    assert(lv_draw_buf_reshape(draw_buf, LV_COLOR_FORMAT_A8, 4U, 4U, 0U) == NULL);
    assert(memcmp(&snapshot, draw_buf, sizeof(snapshot)) == 0);
    assert(lv_draw_buf_reshape(NULL, LV_COLOR_FORMAT_A8, 1U, 1U, 1U) == NULL);

    buffer_free(draw_buf->unaligned_data);
    lv_free(draw_buf);
    assert(buffer_allocations == buffer_frees);
    assert(descriptor_allocations == descriptor_frees);
    return 0;
}
