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
 * NONPRODUCTION bounded Apollo-main adaptation of elog_hexdump() from the
 * authenticated Armink EasyLogger commit
 * a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24. The released G2 seams and
 * uint16_t arithmetic are explicit; this file is not a production input.
 */

#include "runtime_easylogger_hexdump_candidate.h"

static __inline__ const char *open_cfw_easylogger_hexdump_find(
    const char *text,
    const char *needle
)
{
    const char *candidate;

    if (*needle == '\0') {
        return text;
    }
    for (candidate = text; *candidate != '\0'; candidate++) {
        open_cfw_easylogger_hexdump_u32 index = 0U;
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

#define OPEN_CFW_EASYLOGGER_HEXDUMP_APPEND(text) \
    do { \
        log_length += (open_cfw_easylogger_hexdump_u16) \
            open_cfw_easylogger_strcpy( \
                (open_cfw_easylogger_hexdump_u32)log_length, \
                log_buffer + log_length, \
                (text) \
            ); \
    } while (0)

__attribute__((used, noinline))
void open_cfw_easylogger_hexdump_candidate(
    const char *name,
    open_cfw_easylogger_hexdump_u8 width,
    const void *buffer,
    open_cfw_easylogger_hexdump_u16 size
)
{
    struct open_cfw_easylogger_hexdump_logger *logger;
    const open_cfw_easylogger_hexdump_u8 *bytes =
        (const open_cfw_easylogger_hexdump_u8 *)buffer;
    char *log_buffer = (char *)0;
    open_cfw_easylogger_hexdump_u16 offset;
    open_cfw_easylogger_hexdump_u16 index;
    open_cfw_easylogger_hexdump_u16 log_length = 0U;
    char dump_string[8];
    int format_result;

    /* Stock initializes this stack array before reading the logger gates. */
    OPEN_CFW_EASYLOGGER_HEXDUMP_FILL(
        dump_string,
        (open_cfw_easylogger_hexdump_u32)sizeof(dump_string),
        0U
    );

    logger = OPEN_CFW_EASYLOGGER_HEXDUMP_GET_LOGGER();
    if (logger->output_enabled == 0U) {
        return;
    }
    if (logger->filter.level < OPEN_CFW_EASYLOGGER_HEXDUMP_LEVEL_DEBUG) {
        return;
    }
    if (
        open_cfw_easylogger_hexdump_find(name, logger->filter.tag) ==
            (const char *)0
    ) {
        return;
    }

    open_cfw_easylogger_output_lock();

    /*
     * offset and index intentionally remain uint16_t. In particular, width
     * zero with nonzero size repeats the same line, and a non-terminating
     * uint16_t offset sequence wraps exactly like the released body.
     */
    for (offset = 0U; offset < size; offset += width) {
        if (log_buffer == (char *)0) {
            log_buffer = OPEN_CFW_EASYLOGGER_HEXDUMP_GET_BUFFER();
        }
        format_result = OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_HEADER(
            log_buffer,
            OPEN_CFW_EASYLOGGER_HEXDUMP_LINE_BUFFER_SIZE,
            name,
            (unsigned int)offset,
            (unsigned int)offset + (unsigned int)width - 1U
        );
        if (
            format_result > -1 &&
            format_result <= OPEN_CFW_EASYLOGGER_HEXDUMP_LINE_BUFFER_SIZE
        ) {
            log_length = (open_cfw_easylogger_hexdump_u16)format_result;
        } else {
            log_length = OPEN_CFW_EASYLOGGER_HEXDUMP_LINE_BUFFER_SIZE;
        }

        for (index = 0U; index < width; index++) {
            if ((open_cfw_easylogger_hexdump_u32)offset + index < size) {
                OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_HEX(
                    dump_string,
                    bytes[(open_cfw_easylogger_hexdump_u32)
                        offset + index]
                );
            } else {
                OPEN_CFW_EASYLOGGER_HEXDUMP_BLANK_HEX(dump_string);
            }
            OPEN_CFW_EASYLOGGER_HEXDUMP_APPEND(dump_string);
            if (((open_cfw_easylogger_hexdump_u16)(index + 1U) % 8U) == 0U) {
                OPEN_CFW_EASYLOGGER_HEXDUMP_APPEND(" ");
            }
        }

        OPEN_CFW_EASYLOGGER_HEXDUMP_APPEND("  ");
        for (index = 0U; index < width; index++) {
            open_cfw_easylogger_hexdump_u32 position =
                (open_cfw_easylogger_hexdump_u32)offset + index;
            if (position < size) {
                open_cfw_easylogger_hexdump_u8 value = bytes[position];
                OPEN_CFW_EASYLOGGER_HEXDUMP_FORMAT_CHARACTER(
                    dump_string,
                    (open_cfw_easylogger_hexdump_u8)(
                        (unsigned int)(value - (open_cfw_easylogger_hexdump_u8)' ') <
                            (127U - (unsigned int)' ')
                            ? value
                            : (open_cfw_easylogger_hexdump_u8)'.'
                    )
                );
                OPEN_CFW_EASYLOGGER_HEXDUMP_APPEND(dump_string);
            }
        }

        if (
            (open_cfw_easylogger_hexdump_u16)(log_length + 1U) >
                OPEN_CFW_EASYLOGGER_HEXDUMP_LINE_BUFFER_SIZE
        ) {
            log_length = OPEN_CFW_EASYLOGGER_HEXDUMP_LINE_BUFFER_SIZE - 1U;
        }
        OPEN_CFW_EASYLOGGER_HEXDUMP_APPEND("\n");
        OPEN_CFW_EASYLOGGER_HEXDUMP_RAW_SINK(
            log_buffer,
            (open_cfw_easylogger_hexdump_u32)log_length
        );
    }

    open_cfw_easylogger_output_unlock();
}
