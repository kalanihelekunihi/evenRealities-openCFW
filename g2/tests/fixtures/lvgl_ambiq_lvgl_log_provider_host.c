/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_log_provider.h"
#include "src/core/lv_global.h"

#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

lv_global_t lv_global;

static unsigned int fake_tick;
static unsigned int callback_calls;
static lv_log_level_t callback_level;
static char callback_text[512];

int open_cfw_runtime_vsnprintf_wrapper(unsigned char * buffer,
                                       unsigned int count,
                                       const unsigned char * format,
                                       va_list arguments)
{
    return vsnprintf((char *)buffer, count, (const char *)format, arguments);
}

int open_cfw_runtime_snprintf(unsigned char * buffer, unsigned int count,
                              const unsigned char * format, ...)
{
    va_list arguments;
    int result;
    va_start(arguments, format);
    result = vsnprintf((char *)buffer, count, (const char *)format, arguments);
    va_end(arguments);
    return result;
}

unsigned int open_cfw_strlen(const char * text)
{
    return (unsigned int)strlen(text);
}

unsigned int open_cfw_lv_tick_get(void)
{
    return fake_tick;
}

static void print_callback(lv_log_level_t level, const char * text)
{
    callback_calls++;
    callback_level = level;
    (void)snprintf(callback_text, sizeof(callback_text), "%s", text);
}

int main(void)
{
    memset(&lv_global, 0, sizeof(lv_global));
    lv_global.custom_log_print_cb = print_callback;
    lv_global.log_last_log_time = 1000U;
    fake_tick = 2345U;

    lv_log_add(LV_LOG_LEVEL_INFO, "/src/ignored.c", 1, "ignored", "bad");
    assert(callback_calls == 0U);
    assert(lv_global.log_last_log_time == 1000U);
    lv_log_add(LV_LOG_LEVEL_NUM, "/src/ignored.c", 1, "ignored", "bad");
    assert(callback_calls == 0U);

    lv_log_add(LV_LOG_LEVEL_WARN, "/src/draw/lv_draw.c", 466,
               "lv_draw_layer_alloc_buf", "allocation %u", 17U);
    assert(callback_calls == 1U);
    assert(callback_level == LV_LOG_LEVEL_WARN);
    assert(strcmp(callback_text,
                  "[Warn]\t(2.345, +1345)\t lv_draw_layer_alloc_buf: allocation 17 lv_draw.c:466\n") == 0);
    assert(lv_global.log_last_log_time == 2345U);

    fake_tick = 3001U;
    lv_log_add(LV_LOG_LEVEL_ERROR, "plain.c", 9, "decode", "%s %p",
               "failed", (void *)0x1234U);
    assert(callback_calls == 2U);
    assert(callback_level == LV_LOG_LEVEL_ERROR);
    assert(strstr(callback_text, "[Error]\t(3.001, +656)\t decode: failed ") == callback_text);
    assert(strstr(callback_text, " plain.c:9\n") != NULL);

    lv_global.custom_log_print_cb = NULL;
    fake_tick = 4000U;
    lv_log_add(LV_LOG_LEVEL_WARN, "silent.c", 3, "silent", "message");
    assert(callback_calls == 2U);
    assert(lv_global.log_last_log_time == 4000U);

    lv_global.custom_log_print_cb = print_callback;
    lv_log_add(LV_LOG_LEVEL_WARN, NULL, 3, "invalid", "message");
    lv_log_add(LV_LOG_LEVEL_WARN, "file.c", 3, NULL, "message");
    lv_log_add(LV_LOG_LEVEL_WARN, "file.c", 3, "invalid", NULL);
    assert(callback_calls == 2U);
    assert(lv_global.log_last_log_time == 4000U);
    return 0;
}
