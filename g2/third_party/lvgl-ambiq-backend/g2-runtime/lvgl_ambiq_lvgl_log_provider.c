/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounded transcription of lv_log_add from authenticated LVGL commit
 * 344c7c318047b7348e1be8572a9fd4260c251cfa. It preserves the recovered G2
 * callback, timestamp, file/line, and WARN-level policy while using the
 * already maintained production formatter, string, and tick sources.
 */

#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>

#include "lvgl_ambiq_lvgl_log_provider.h"
#include "src/core/lv_global.h"

#if LV_USE_LOG != 1
#error "G2 logging provider requires the recovered enabled logging policy"
#endif
#if LV_LOG_PRINTF != 0
#error "G2 logging provider requires callback-mode logging"
#endif
#if LV_LOG_USE_TIMESTAMP != 1
#error "G2 logging provider requires timestamps"
#endif
#if LV_LOG_USE_FILE_LINE != 1
#error "G2 logging provider requires file/line output"
#endif
#if LV_LOG_LEVEL != LV_LOG_LEVEL_WARN
#error "G2 logging provider requires the recovered WARN threshold"
#endif

int open_cfw_runtime_vsnprintf_wrapper(unsigned char * buffer,
                                       unsigned int count,
                                       const unsigned char * format,
                                       va_list arguments);
int open_cfw_runtime_snprintf(unsigned char * buffer, unsigned int count,
                              const unsigned char * format, ...);
unsigned int open_cfw_strlen(const char * text);
unsigned int open_cfw_lv_tick_get(void);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(lv_global_t, custom_log_print_cb) == 0x16CU,
               "G2 log callback offset changed");
_Static_assert(offsetof(lv_global_t, log_last_log_time) == 0x170U,
               "G2 log timestamp offset changed");
#endif

void lv_log_add(lv_log_level_t level, const char * file, int line,
                const char * function, const char * format, ...)
{
    static const char * const level_prefix[] = {
        "Trace", "Info", "Warn", "Error", "User",
    };
    lv_global_t * global;
    lv_log_print_g_cb_t callback;
    unsigned int file_offset;
    unsigned int now;
    va_list arguments;

    if(level >= LV_LOG_LEVEL_NUM || level < LV_LOG_LEVEL) return;
    if(file == NULL || function == NULL || format == NULL) return;

    file_offset = open_cfw_strlen(file);
    while(file_offset > 0U) {
        const char character = file[file_offset];
        if(character == '/' || character == '\\') {
            file_offset++;
            break;
        }
        file_offset--;
    }

    global = LV_GLOBAL_DEFAULT();
    now = open_cfw_lv_tick_get();
    callback = global->custom_log_print_cb;
    va_start(arguments, format);
    if(callback != NULL) {
        unsigned char message[256];
        unsigned char buffer[512];

        (void)open_cfw_runtime_vsnprintf_wrapper(
            message, sizeof(message), (const unsigned char *)format, arguments);
        (void)open_cfw_runtime_snprintf(
            buffer, sizeof(buffer),
            (const unsigned char *)"[%s]\t(%u.%03u, +%u)\t %s: %s %s:%d\n",
            level_prefix[level], now / 1000U, now % 1000U,
            now - global->log_last_log_time, function, message,
            &file[file_offset], line);
        callback(level, (const char *)buffer);
    }
    global->log_last_log_time = now;
    va_end(arguments);
}
