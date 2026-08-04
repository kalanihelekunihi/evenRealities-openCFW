/*
 * This file is part of the EasyLogger Library.
 *
 * Copyright (c) 2015-2018, Armink, <armink.ztl@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 *
 * Production bounded Apollo-main adaptation of elog_output() from the
 * authenticated Armink EasyLogger commit
 * a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24 (elog.c Git blob
 * b3a00e3927edf97013ddfffeb157be5c1462a6b4). Focused G2 disassembly adds the
 * exception-context no-op gate and preserves the level-aware G2 async ABI.
 * elog_hexdump() is intentionally outside this source boundary.
 */

#include "runtime_easylogger_output_candidate.h"

static __inline__ open_cfw_easylogger_output_u32
open_cfw_easylogger_output_length(const char *text)
{
    open_cfw_easylogger_output_u32 length = 0U;
    while (text[length] != '\0') {
        length++;
    }
    return length;
}

static __inline__ const char *open_cfw_easylogger_output_find(
    const char *text,
    const char *needle
)
{
    const char *candidate;

    if (*needle == '\0') {
        return text;
    }
    for (candidate = text; *candidate != '\0'; candidate++) {
        open_cfw_easylogger_output_u32 index = 0U;
        while (
            needle[index] != '\0' &&
            candidate[index] == needle[index]
        ) {
            index++;
        }
        if (needle[index] == '\0') {
            return candidate;
        }
    }
    return (const char *)0;
}

static __inline__ void open_cfw_easylogger_output_fill(
    char *destination,
    char value,
    open_cfw_easylogger_output_u32 count
)
{
    open_cfw_easylogger_output_u32 index;
    for (index = 0U; index < count; index++) {
        destination[index] = value;
    }
}

static __inline__ const char *open_cfw_easylogger_output_level_text(
    open_cfw_easylogger_output_u8 level
)
{
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_ASSERT) {
        return "A/";
    }
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_ERROR) {
        return "E/";
    }
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_WARN) {
        return "W/";
    }
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_INFO) {
        return "I/";
    }
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_DEBUG) {
        return "D/";
    }
    return "V/";
}

static __inline__ const char *open_cfw_easylogger_output_color_text(
    open_cfw_easylogger_output_u8 level
)
{
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_ASSERT) {
        return "35;22m";
    }
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_ERROR) {
        return "31;22m";
    }
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_WARN) {
        return "33;22m";
    }
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_INFO) {
        return "36;22m";
    }
    if (level == OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_DEBUG) {
        return "32;22m";
    }
    return "34;22m";
}

#define OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(text) \
    do { \
        log_length += open_cfw_easylogger_strcpy( \
            log_length, log_buffer + log_length, (text) \
        ); \
    } while (0)

__attribute__((used, noinline))
void open_cfw_easylogger_output(
    open_cfw_easylogger_output_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...
)
{
    struct open_cfw_easylogger_output_logger *logger;
    char *log_buffer;
    open_cfw_easylogger_output_u32 tag_length;
    open_cfw_easylogger_output_u32 log_length = 0U;
    char line_number[OPEN_CFW_EASYLOGGER_OUTPUT_LINE_NUMBER_MAX + 1];
    char tag_space[OPEN_CFW_EASYLOGGER_OUTPUT_TAG_MAX / 2 + 1];
    open_cfw_easylogger_output_va_list arguments;
    int format_result;

    /* This must remain the first semantic operation in the target body. */
    if (OPEN_CFW_EASYLOGGER_OUTPUT_READ_IPSR() != 0U) {
        return;
    }

    if (level > OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_VERBOSE) {
        open_cfw_easylogger_output_assert_hook_fn hook =
            OPEN_CFW_EASYLOGGER_OUTPUT_GET_ASSERT_HOOK();
        if (hook != (open_cfw_easylogger_output_assert_hook_fn)0) {
            hook(
                "level <= ELOG_LVL_VERBOSE",
                "elog_output",
                OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_LINE
            );
        } else {
            open_cfw_easylogger_output(
                OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_ASSERT,
                "elog",
                OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_SOURCE_PATH,
                "elog_output",
                OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_LINE,
                "(%s) has assert failed at %s:%ld.",
                "level <= ELOG_LVL_VERBOSE",
                "elog_output",
                (long)OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_LINE
            );
            for (;;) {
                OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_WAIT();
            }
        }
    }

    logger = OPEN_CFW_EASYLOGGER_OUTPUT_GET_LOGGER();
    if (logger->output_enabled == 0U) {
        return;
    }
    if (
        level > logger->filter.level ||
        level > open_cfw_easylogger_get_filter_tag_level(tag)
    ) {
        return;
    }
    if (
        open_cfw_easylogger_output_find(tag, logger->filter.tag) ==
            (const char *)0
    ) {
        return;
    }

    tag_length = open_cfw_easylogger_output_length(tag);
    open_cfw_easylogger_output_fill(
        line_number,
        '\0',
        (open_cfw_easylogger_output_u32)sizeof(line_number)
    );
    open_cfw_easylogger_output_fill(
        tag_space,
        '\0',
        (open_cfw_easylogger_output_u32)sizeof(tag_space)
    );
    __builtin_va_start(arguments, format);
    open_cfw_easylogger_output_lock();
    log_buffer = OPEN_CFW_EASYLOGGER_OUTPUT_GET_BUFFER();

    if (logger->text_color_enabled != 0U) {
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND("\x1b[");
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(
            open_cfw_easylogger_output_color_text(level)
        );
    }

    if (
        open_cfw_easylogger_get_fmt_enabled(
            level,
            OPEN_CFW_EASYLOGGER_OUTPUT_FMT_LEVEL
        ) != 0U
    ) {
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(
            open_cfw_easylogger_output_level_text(level)
        );
    }

    if (
        open_cfw_easylogger_get_fmt_enabled(
            level,
            OPEN_CFW_EASYLOGGER_OUTPUT_FMT_TAG
        ) != 0U
    ) {
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(tag);
        if (tag_length <= OPEN_CFW_EASYLOGGER_OUTPUT_TAG_MAX / 2U) {
            open_cfw_easylogger_output_fill(
                tag_space,
                ' ',
                OPEN_CFW_EASYLOGGER_OUTPUT_TAG_MAX / 2U - tag_length
            );
            OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(tag_space);
        }
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(" ");
    }

    if (
        open_cfw_easylogger_get_fmt_enabled(
            level,
            OPEN_CFW_EASYLOGGER_OUTPUT_FMT_TIME |
                OPEN_CFW_EASYLOGGER_OUTPUT_FMT_PROCESS |
                OPEN_CFW_EASYLOGGER_OUTPUT_FMT_THREAD
        ) != 0U
    ) {
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND("[");
        if (
            open_cfw_easylogger_get_fmt_enabled(
                level,
                OPEN_CFW_EASYLOGGER_OUTPUT_FMT_TIME
            ) != 0U
        ) {
            OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(
                OPEN_CFW_EASYLOGGER_OUTPUT_GET_TIME()
            );
            if (
                open_cfw_easylogger_get_fmt_enabled(
                    level,
                    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_PROCESS |
                        OPEN_CFW_EASYLOGGER_OUTPUT_FMT_THREAD
                ) != 0U
            ) {
                OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(" ");
            }
        }
        if (
            open_cfw_easylogger_get_fmt_enabled(
                level,
                OPEN_CFW_EASYLOGGER_OUTPUT_FMT_PROCESS
            ) != 0U
        ) {
            OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(
                OPEN_CFW_EASYLOGGER_OUTPUT_GET_PROCESS()
            );
            if (
                open_cfw_easylogger_get_fmt_enabled(
                    level,
                    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_THREAD
                ) != 0U
            ) {
                OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(" ");
            }
        }
        if (
            open_cfw_easylogger_get_fmt_enabled(
                level,
                OPEN_CFW_EASYLOGGER_OUTPUT_FMT_THREAD
            ) != 0U
        ) {
            OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(
                OPEN_CFW_EASYLOGGER_OUTPUT_GET_THREAD()
            );
        }
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND("] ");
    }

    if (
        open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
            level,
            OPEN_CFW_EASYLOGGER_OUTPUT_FMT_DIRECTORY,
            file
        ) != 0U ||
        open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
            level,
            OPEN_CFW_EASYLOGGER_OUTPUT_FMT_FUNCTION,
            function
        ) != 0U ||
        open_cfw_easylogger_get_fmt_used_and_enabled_u32(
            level,
            OPEN_CFW_EASYLOGGER_OUTPUT_FMT_LINE,
            (open_cfw_easylogger_output_u32)line
        ) != 0U
    ) {
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND("(");
        if (
            open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
                level,
                OPEN_CFW_EASYLOGGER_OUTPUT_FMT_DIRECTORY,
                file
            ) != 0U
        ) {
            OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(file);
            if (
                open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
                    level,
                    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_FUNCTION,
                    function
                ) != 0U
            ) {
                OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(":");
            } else if (
                open_cfw_easylogger_get_fmt_used_and_enabled_u32(
                    level,
                    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_LINE,
                    (open_cfw_easylogger_output_u32)line
                ) != 0U
            ) {
                OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(" ");
            }
        }
        if (
            open_cfw_easylogger_get_fmt_used_and_enabled_u32(
                level,
                OPEN_CFW_EASYLOGGER_OUTPUT_FMT_LINE,
                (open_cfw_easylogger_output_u32)line
            ) != 0U
        ) {
            (void)OPEN_CFW_EASYLOGGER_OUTPUT_SNPRINTF(
                line_number,
                OPEN_CFW_EASYLOGGER_OUTPUT_LINE_NUMBER_MAX,
                "%ld",
                line
            );
            OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(line_number);
            if (
                open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
                    level,
                    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_FUNCTION,
                    function
                ) != 0U
            ) {
                OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(" ");
            }
        }
        if (
            open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
                level,
                OPEN_CFW_EASYLOGGER_OUTPUT_FMT_FUNCTION,
                function
            ) != 0U
        ) {
            OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(function);
        }
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND(")");
    }

    format_result = OPEN_CFW_EASYLOGGER_OUTPUT_VSNPRINTF(
        log_buffer + log_length,
        OPEN_CFW_EASYLOGGER_OUTPUT_LINE_BUFFER_SIZE - log_length,
        format,
        arguments
    );
    __builtin_va_end(arguments);

    if (
        log_length + (open_cfw_easylogger_output_u32)format_result <=
            OPEN_CFW_EASYLOGGER_OUTPUT_LINE_BUFFER_SIZE &&
        format_result > -1
    ) {
        log_length += (open_cfw_easylogger_output_u32)format_result;
    } else {
        log_length = OPEN_CFW_EASYLOGGER_OUTPUT_LINE_BUFFER_SIZE;
    }

    if (
        log_length + 4U + 1U >
            OPEN_CFW_EASYLOGGER_OUTPUT_LINE_BUFFER_SIZE
    ) {
        log_length = OPEN_CFW_EASYLOGGER_OUTPUT_LINE_BUFFER_SIZE - 4U - 1U;
    }

    if (logger->filter.keyword[0] != '\0') {
        log_buffer[log_length] = '\0';
        if (
            open_cfw_easylogger_output_find(
                log_buffer,
                logger->filter.keyword
            ) == (const char *)0
        ) {
            open_cfw_easylogger_output_unlock();
            return;
        }
    }

    if (logger->text_color_enabled != 0U) {
        OPEN_CFW_EASYLOGGER_OUTPUT_APPEND("\x1b[0m");
    }
    OPEN_CFW_EASYLOGGER_OUTPUT_APPEND("\n");
    open_cfw_g2_easylogger_async_submit(log_buffer, log_length, level);
    open_cfw_easylogger_output_unlock();
}

#undef OPEN_CFW_EASYLOGGER_OUTPUT_APPEND
