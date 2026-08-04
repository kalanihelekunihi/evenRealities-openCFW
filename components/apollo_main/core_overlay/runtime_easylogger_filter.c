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
 * Bounded Apollo-main adaptation of the EasyLogger tag-level reset and lookup
 * algorithms from authenticated snapshot
 * a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24.  Focused G2 disassembly recovers
 * the five-entry configuration, 30-byte comparison bound, object address, and
 * assertion ABI.  Private byte loops keep memset/strncmp outside this source
 * boundary; output locking resolves directly to the existing source port.
 */

typedef __UINT8_TYPE__ open_cfw_easylogger_filter_u8;
typedef __UINT32_TYPE__ open_cfw_easylogger_filter_u32;
typedef __UINTPTR_TYPE__ open_cfw_easylogger_filter_uintptr;

enum {
    OPEN_CFW_EASYLOGGER_FILTER_CORE_LEVEL_SILENT = 0,
    OPEN_CFW_EASYLOGGER_FILTER_CORE_LEVEL_ALL = 5,
    OPEN_CFW_EASYLOGGER_FILTER_CORE_TAG_MAX = 30,
    OPEN_CFW_EASYLOGGER_FILTER_CORE_KEYWORD_MAX = 16,
    OPEN_CFW_EASYLOGGER_FILTER_CORE_TAG_LEVEL_MAX = 5
};

struct open_cfw_easylogger_filter_tag_level {
    open_cfw_easylogger_filter_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_FILTER_CORE_TAG_MAX + 1];
    open_cfw_easylogger_filter_u8 tag_use_flag;
};

struct open_cfw_easylogger_filter_state {
    open_cfw_easylogger_filter_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_FILTER_CORE_TAG_MAX + 1];
    char keyword[OPEN_CFW_EASYLOGGER_FILTER_CORE_KEYWORD_MAX + 1];
    struct open_cfw_easylogger_filter_tag_level
        tag_level[OPEN_CFW_EASYLOGGER_FILTER_CORE_TAG_LEVEL_MAX];
};

struct open_cfw_easylogger_filter_logger {
    struct open_cfw_easylogger_filter_state filter;
    open_cfw_easylogger_filter_u32 enabled_format_set[6];
    open_cfw_easylogger_filter_u8 init_ok;
    open_cfw_easylogger_filter_u8 output_enabled;
    open_cfw_easylogger_filter_u8 output_lock_enabled;
    open_cfw_easylogger_filter_u8 output_is_locked_before_enable;
    open_cfw_easylogger_filter_u8 output_is_locked_before_disable;
    open_cfw_easylogger_filter_u8 text_color_enabled;
};

_Static_assert(
    sizeof(struct open_cfw_easylogger_filter_tag_level) == 0x21U,
    "G2 ElogTagLvlFilter ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_filter_state) == 0xD6U,
    "G2 ElogFilter ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_filter_logger,
        filter.tag_level
    ) == 0x31U,
    "G2 tag-level table offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_filter_logger,
        init_ok
    ) == 0xF0U,
    "G2 EasyLogger init flag offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_filter_logger) == 0xF8U,
    "G2 EasyLogger ABI changed"
);

#ifndef OPEN_CFW_EASYLOGGER_FILTER_STATE
#define OPEN_CFW_EASYLOGGER_FILTER_STATE() \
    ((struct open_cfw_easylogger_filter_logger *) \
        (open_cfw_easylogger_filter_uintptr)0x20070BE8U)
#endif

typedef void (*open_cfw_easylogger_filter_assert_hook_fn)(
    const char *expression,
    const char *function,
    open_cfw_easylogger_filter_u32 line
);

typedef void (*open_cfw_easylogger_filter_output_fn)(
    open_cfw_easylogger_filter_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...
);

typedef void (*open_cfw_easylogger_filter_void_fn)(void);

#ifndef OPEN_CFW_EASYLOGGER_FILTER_ASSERT_HOOK
#define OPEN_CFW_EASYLOGGER_FILTER_ASSERT_HOOK() \
    (*(open_cfw_easylogger_filter_assert_hook_fn volatile *) \
        (open_cfw_easylogger_filter_uintptr)0x2007456CU)
#endif

#ifndef OPEN_CFW_EASYLOGGER_FILTER_ASSERT_OUTPUT
#define OPEN_CFW_EASYLOGGER_FILTER_ASSERT_OUTPUT( \
    expression, \
    function, \
    line \
) \
    (((open_cfw_easylogger_filter_output_fn) \
        (open_cfw_easylogger_filter_uintptr)0x0043D575U)( \
            0U, \
            "elog", \
            (const char *) \
                (open_cfw_easylogger_filter_uintptr)0x006E3098U, \
            (function), \
            (long)(line), \
            "(%s) has assert failed at %s:%ld.", \
            (expression), \
            (function), \
            (long)(line) \
        ))
#endif

#ifndef OPEN_CFW_EASYLOGGER_FILTER_ASSERT_WAIT
#define OPEN_CFW_EASYLOGGER_FILTER_ASSERT_WAIT() \
    (((open_cfw_easylogger_filter_void_fn) \
        (open_cfw_easylogger_filter_uintptr)0x0044B0AFU)())
#endif

#ifndef OPEN_CFW_EASYLOGGER_FILTER_ASSERT_FAILED
#define OPEN_CFW_EASYLOGGER_FILTER_ASSERT_FAILED( \
    expression, \
    function, \
    line \
) \
    do { \
        open_cfw_easylogger_filter_assert_hook_fn open_cfw_hook = \
            OPEN_CFW_EASYLOGGER_FILTER_ASSERT_HOOK(); \
        if ( \
            open_cfw_hook != \
                (open_cfw_easylogger_filter_assert_hook_fn)0 \
        ) { \
            open_cfw_hook((expression), (function), (line)); \
        } else { \
            OPEN_CFW_EASYLOGGER_FILTER_ASSERT_OUTPUT( \
                (expression), \
                (function), \
                (line) \
            ); \
            for (;;) { \
                OPEN_CFW_EASYLOGGER_FILTER_ASSERT_WAIT(); \
            } \
        } \
    } while (0)
#endif

extern void open_cfw_easylogger_output_lock(void);
extern void open_cfw_easylogger_output_unlock(void);

__attribute__((noinline))
static void open_cfw_easylogger_filter_zero_tag(char *tag)
{
    open_cfw_easylogger_filter_u32 index;

    for (
        index = 0U;
        index <= OPEN_CFW_EASYLOGGER_FILTER_CORE_TAG_MAX;
        index++
    ) {
        tag[index] = '\0';
    }
}

__attribute__((noinline))
static open_cfw_easylogger_filter_u8
open_cfw_easylogger_filter_tags_equal(
    const char *left,
    const char *right
)
{
    open_cfw_easylogger_filter_u32 index;

    for (
        index = 0U;
        index < OPEN_CFW_EASYLOGGER_FILTER_CORE_TAG_MAX;
        index++
    ) {
        open_cfw_easylogger_filter_u8 left_byte =
            (open_cfw_easylogger_filter_u8)left[index];
        open_cfw_easylogger_filter_u8 right_byte =
            (open_cfw_easylogger_filter_u8)right[index];

        if (left_byte != right_byte) {
            return 0U;
        }
        if (left_byte == 0U) {
            return 1U;
        }
    }
    return 1U;
}

__attribute__((used, noinline))
void open_cfw_easylogger_filter_tag_levels_reset(void)
{
    struct open_cfw_easylogger_filter_logger *logger =
        OPEN_CFW_EASYLOGGER_FILTER_STATE();
    open_cfw_easylogger_filter_u32 index;

    for (
        index = 0U;
        index < OPEN_CFW_EASYLOGGER_FILTER_CORE_TAG_LEVEL_MAX;
        index++
    ) {
        open_cfw_easylogger_filter_zero_tag(
            logger->filter.tag_level[index].tag
        );
        logger->filter.tag_level[index].level =
            OPEN_CFW_EASYLOGGER_FILTER_CORE_LEVEL_SILENT;
        logger->filter.tag_level[index].tag_use_flag = 0U;
    }
}

__attribute__((used, noinline))
open_cfw_easylogger_filter_u8 open_cfw_easylogger_get_filter_tag_level(
    const char *tag
)
{
    struct open_cfw_easylogger_filter_logger *logger =
        OPEN_CFW_EASYLOGGER_FILTER_STATE();
    open_cfw_easylogger_filter_u8 level =
        OPEN_CFW_EASYLOGGER_FILTER_CORE_LEVEL_ALL;
    open_cfw_easylogger_filter_u32 index;

    if (tag == (const char *)0) {
        OPEN_CFW_EASYLOGGER_FILTER_ASSERT_FAILED(
            "tag != ((void *)0)",
            "elog_get_filter_tag_lvl",
            481U
        );
    }

    if (logger->init_ok == 0U) {
        return level;
    }

    open_cfw_easylogger_output_lock();
    for (
        index = 0U;
        index < OPEN_CFW_EASYLOGGER_FILTER_CORE_TAG_LEVEL_MAX;
        index++
    ) {
        if (
            (logger->filter.tag_level[index].tag_use_flag != 0U) &&
            (
                open_cfw_easylogger_filter_tags_equal(
                    tag,
                    logger->filter.tag_level[index].tag
                ) != 0U
            )
        ) {
            level = logger->filter.tag_level[index].level;
            break;
        }
    }
    open_cfw_easylogger_output_unlock();

    return level;
}
