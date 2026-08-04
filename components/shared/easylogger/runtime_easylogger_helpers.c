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
 * Bounded dual-image adaptation of elog_strcpy(), get_fmt_enabled(), and its
 * argument-aware predicates from authenticated Armink EasyLogger commit
 * a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24. The only recovered G2
 * configuration applied to the algorithms is a 32-bit size_t/format set, six
 * log levels, ELOG_LINE_BUF_SIZE == 1024, the standard logger object layout,
 * and the released image's assertion line metadata.
 */

#include "runtime_easylogger_helpers.h"

#if defined(OPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF) && \
    (defined(OPEN_CFW_EASYLOGGER_HELPERS_LEAF_STRCPY) + \
        defined(OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_ENABLED) + \
        defined( \
            OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_USED_AND_ENABLED_U32 \
        ) + \
        defined( \
            OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_USED_AND_ENABLED_PTR \
        )) != 1
#error "select exactly one EasyLogger helper leaf"
#endif

#if !defined(OPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF) || \
    defined(OPEN_CFW_EASYLOGGER_HELPERS_LEAF_STRCPY)
__attribute__((used, noinline))
open_cfw_easylogger_helpers_u32 open_cfw_easylogger_strcpy(
    open_cfw_easylogger_helpers_u32 current_length,
    char *destination,
    const char *source
)
{
    const char *source_old = source;

    if (destination == (char *)0) {
        OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_FAILED(
            OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_DST_LINE
        );
    }
    if (source == (const char *)0) {
        OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_FAILED(
            OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_SRC_LINE
        );
    }

    while (*source != '\0') {
        if (
            current_length++ <
                OPEN_CFW_EASYLOGGER_HELPERS_LINE_BUFFER_SIZE
        ) {
            *destination++ = *source++;
        } else {
            break;
        }
    }

    return (open_cfw_easylogger_helpers_u32)(source - source_old);
}
#endif

#if !defined(OPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF) || \
    defined(OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_ENABLED)
__attribute__((used, noinline))
open_cfw_easylogger_helpers_u8 open_cfw_easylogger_get_fmt_enabled(
    open_cfw_easylogger_helpers_u8 level,
    open_cfw_easylogger_helpers_u32 format_set
)
{
    struct open_cfw_easylogger_helpers_logger *logger;

    if (level > OPEN_CFW_EASYLOGGER_HELPERS_LEVEL_VERBOSE) {
        OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_FAILED(
            OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_GET_FMT_LINE
        );
    }

    logger = OPEN_CFW_EASYLOGGER_HELPERS_GET_LOGGER();
    return (open_cfw_easylogger_helpers_u8)(
        (logger->enabled_format_set[level] & format_set) != 0U
    );
}
#endif

#if !defined(OPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF) || \
    defined( \
        OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_USED_AND_ENABLED_U32 \
    )
__attribute__((used, noinline))
open_cfw_easylogger_helpers_u8
open_cfw_easylogger_get_fmt_used_and_enabled_u32(
    open_cfw_easylogger_helpers_u8 level,
    open_cfw_easylogger_helpers_u32 format_set,
    open_cfw_easylogger_helpers_u32 argument
)
{
    return (open_cfw_easylogger_helpers_u8)(
        argument != 0U &&
        open_cfw_easylogger_get_fmt_enabled(level, format_set) != 0U
    );
}
#endif

#if !defined(OPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF) || \
    defined( \
        OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_USED_AND_ENABLED_PTR \
    )
__attribute__((used, noinline))
open_cfw_easylogger_helpers_u8
open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
    open_cfw_easylogger_helpers_u8 level,
    open_cfw_easylogger_helpers_u32 format_set,
    const char *argument
)
{
    return (open_cfw_easylogger_helpers_u8)(
        argument != (const char *)0 &&
        open_cfw_easylogger_get_fmt_enabled(level, format_set) != 0U
    );
}
#endif
