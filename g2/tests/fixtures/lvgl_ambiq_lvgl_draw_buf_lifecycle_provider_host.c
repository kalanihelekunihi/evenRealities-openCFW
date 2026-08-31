/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_draw_buf_lifecycle_provider.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static unsigned buffer_free_calls;
static unsigned descriptor_free_calls;
static void * last_buffer;
static void * last_descriptor;

static void buffer_free(void * buffer)
{
    buffer_free_calls++;
    last_buffer = buffer;
}

void lv_free(void * pointer)
{
    descriptor_free_calls++;
    last_descriptor = pointer;
}

int main(void)
{
    lv_draw_buf_handlers_t handlers;
    lv_draw_buf_t draw_buf;
    uint8_t storage[8];

    memset(&handlers, 0, sizeof(handlers));
    memset(&draw_buf, 0, sizeof(draw_buf));

    lv_draw_buf_destroy(NULL);
    assert(buffer_free_calls == 0U && descriptor_free_calls == 0U);

    draw_buf.handlers = &handlers;
    draw_buf.unaligned_data = storage;
    lv_draw_buf_destroy(&draw_buf);
    assert(buffer_free_calls == 0U && descriptor_free_calls == 0U);

    draw_buf.header.flags = LV_IMAGE_FLAGS_ALLOCATED;
    draw_buf.handlers = NULL;
    lv_draw_buf_destroy(&draw_buf);
    assert(buffer_free_calls == 0U && descriptor_free_calls == 0U);

    draw_buf.handlers = &handlers;
    lv_draw_buf_destroy(&draw_buf);
    assert(buffer_free_calls == 0U && descriptor_free_calls == 1U);
    assert(last_descriptor == &draw_buf);

    handlers.buf_free_cb = buffer_free;
    lv_draw_buf_destroy(&draw_buf);
    assert(buffer_free_calls == 1U && descriptor_free_calls == 2U);
    assert(last_buffer == storage && last_descriptor == &draw_buf);

    draw_buf.unaligned_data = NULL;
    lv_draw_buf_destroy(&draw_buf);
    assert(buffer_free_calls == 2U && descriptor_free_calls == 3U);
    assert(last_buffer == NULL);
    return 0;
}
