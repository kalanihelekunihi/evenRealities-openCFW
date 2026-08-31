/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdint.h>
#include <string.h>

#include "src/libs/freetype/lv_freetype_private.h"
#include "lvgl_ambiq_lvgl_freetype_event_provider.h"

static lv_freetype_context_t context;
static lv_freetype_context_t * selected_context;

lv_freetype_context_t * open_cfw_test_freetype_context(void)
{
    return selected_context;
}

static void callback_a(lv_event_t * event)
{
    (void)event;
}

static void callback_b(lv_event_t * event)
{
    (void)event;
}

int main(void)
{
    unsigned int marker = 0xA5A55A5AU;

    memset(&context, 0, sizeof(context));
    selected_context = NULL;
    lv_freetype_outline_add_event(callback_a, LV_EVENT_ALL, &marker);

    selected_context = &context;
    lv_freetype_outline_add_event(callback_a, LV_EVENT_ALL, &marker);
    assert(context.event_cb == callback_a);

    lv_freetype_outline_add_event(callback_b, (lv_event_code_t)0, NULL);
    assert(context.event_cb == callback_b);

    lv_freetype_outline_add_event(NULL, (lv_event_code_t)UINT16_MAX, &marker);
    assert(context.event_cb == NULL);
    assert(marker == 0xA5A55A5AU);
    return 0;
}
