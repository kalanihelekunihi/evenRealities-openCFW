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
 * Bounded Apollo-main adaptation of the EasyLogger 2.2.99-labeled control
 * functions from the authenticated a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24
 * snapshot.  The algorithms below intentionally preserve the pristine
 * upstream control flow while binding it to the recovered G2 object ABI.
 *
 * The G2 asynchronous transport is not implemented here.  The existing stock
 * assertion output, delay, C-library copy, and Apollo port lock/unlock entries
 * remain explicit seams until their respective source boundaries are ready.
 */

typedef __UINT8_TYPE__ open_cfw_easylogger_u8;
typedef __UINT32_TYPE__ open_cfw_easylogger_u32;
typedef __UINTPTR_TYPE__ open_cfw_easylogger_uintptr;

enum {
    OPEN_CFW_EASYLOGGER_LEVEL_VERBOSE = 5,
    OPEN_CFW_EASYLOGGER_LEVEL_TOTAL = 6,
    OPEN_CFW_EASYLOGGER_FILTER_TAG_MAX = 30,
    OPEN_CFW_EASYLOGGER_FILTER_KEYWORD_MAX = 16,
    OPEN_CFW_EASYLOGGER_FILTER_TAG_LEVEL_MAX = 5
};

struct open_cfw_easylogger_tag_level {
    open_cfw_easylogger_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_FILTER_TAG_MAX + 1];
    open_cfw_easylogger_u8 tag_use_flag;
};

struct open_cfw_easylogger_filter {
    open_cfw_easylogger_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_FILTER_TAG_MAX + 1];
    char keyword[OPEN_CFW_EASYLOGGER_FILTER_KEYWORD_MAX + 1];
    struct open_cfw_easylogger_tag_level
        tag_level[OPEN_CFW_EASYLOGGER_FILTER_TAG_LEVEL_MAX];
};

struct open_cfw_easylogger {
    struct open_cfw_easylogger_filter filter;
    open_cfw_easylogger_u32 enabled_format_set[
        OPEN_CFW_EASYLOGGER_LEVEL_TOTAL
    ];
    open_cfw_easylogger_u8 init_ok;
    open_cfw_easylogger_u8 output_enabled;
    open_cfw_easylogger_u8 output_lock_enabled;
    open_cfw_easylogger_u8 output_is_locked_before_enable;
    open_cfw_easylogger_u8 output_is_locked_before_disable;
    open_cfw_easylogger_u8 text_color_enabled;
};

_Static_assert(
    sizeof(struct open_cfw_easylogger_tag_level) == 0x21U,
    "G2 ElogTagLvlFilter ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_filter) == 0xD6U,
    "G2 ElogFilter ABI changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger, enabled_format_set) ==
        0xD8U,
    "G2 enabled-format offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger, init_ok) == 0xF0U,
    "G2 init flag offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger, output_enabled) ==
        0xF1U,
    "G2 output-enabled offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger, output_lock_enabled) ==
        0xF2U,
    "G2 lock-enabled offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger,
        output_is_locked_before_enable
    ) == 0xF3U,
    "G2 before-enable lock flag offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger,
        output_is_locked_before_disable
    ) == 0xF4U,
    "G2 before-disable lock flag offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_easylogger, text_color_enabled) ==
        0xF5U,
    "G2 text-color flag offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger) == 0xF8U,
    "G2 EasyLogger ABI changed"
);

#ifndef OPEN_CFW_EASYLOGGER_STATE
#define OPEN_CFW_EASYLOGGER_STATE() \
    ((struct open_cfw_easylogger *)(open_cfw_easylogger_uintptr)0x20070BE8U)
#endif

typedef void (*open_cfw_easylogger_assert_hook_fn)(
    const char *expression,
    const char *function,
    open_cfw_easylogger_u32 line
);

typedef void (*open_cfw_easylogger_output_fn)(
    open_cfw_easylogger_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...
);

typedef void (*open_cfw_easylogger_void_fn)(void);
typedef char *(*open_cfw_easylogger_strncpy_fn)(
    char *destination,
    const char *source,
    open_cfw_easylogger_u32 count
);

#ifndef OPEN_CFW_EASYLOGGER_ASSERT_HOOK
#define OPEN_CFW_EASYLOGGER_ASSERT_HOOK() \
    (*(open_cfw_easylogger_assert_hook_fn volatile *) \
        (open_cfw_easylogger_uintptr)0x2007456CU)
#endif

#ifndef OPEN_CFW_EASYLOGGER_ASSERT_OUTPUT
#define OPEN_CFW_EASYLOGGER_ASSERT_OUTPUT( \
    expression, \
    function, \
    line \
) \
    (((open_cfw_easylogger_output_fn) \
        (open_cfw_easylogger_uintptr)0x0043D575U)( \
            0U, \
            "elog", \
            (const char *)(open_cfw_easylogger_uintptr)0x006E3098U, \
            (function), \
            (long)(line), \
            "(%s) has assert failed at %s:%ld.", \
            (expression), \
            (function), \
            (long)(line) \
        ))
#endif

#ifndef OPEN_CFW_EASYLOGGER_ASSERT_WAIT
#define OPEN_CFW_EASYLOGGER_ASSERT_WAIT() \
    (((open_cfw_easylogger_void_fn) \
        (open_cfw_easylogger_uintptr)0x0044B0AFU)())
#endif

#ifndef OPEN_CFW_EASYLOGGER_FILTER_COPY
#define OPEN_CFW_EASYLOGGER_FILTER_COPY(destination, source, count) \
    (((open_cfw_easylogger_strncpy_fn) \
        (open_cfw_easylogger_uintptr)0x0044B5A1U)( \
            (destination), \
            (source), \
            (count) \
        ))
#endif

#ifndef OPEN_CFW_EASYLOGGER_PORT_LOCK
#define OPEN_CFW_EASYLOGGER_PORT_LOCK() \
    (((open_cfw_easylogger_void_fn) \
        (open_cfw_easylogger_uintptr)0x0044AA99U)())
#endif

#ifndef OPEN_CFW_EASYLOGGER_PORT_UNLOCK
#define OPEN_CFW_EASYLOGGER_PORT_UNLOCK() \
    (((open_cfw_easylogger_void_fn) \
        (open_cfw_easylogger_uintptr)0x0044AAA1U)())
#endif

#ifndef OPEN_CFW_EASYLOGGER_ASSERT_FAILED
#define OPEN_CFW_EASYLOGGER_ASSERT_FAILED( \
    expression, \
    function, \
    line \
) \
    do { \
        open_cfw_easylogger_assert_hook_fn open_cfw_hook = \
            OPEN_CFW_EASYLOGGER_ASSERT_HOOK(); \
        if (open_cfw_hook != (open_cfw_easylogger_assert_hook_fn)0) { \
            open_cfw_hook((expression), (function), (line)); \
        } else { \
            OPEN_CFW_EASYLOGGER_ASSERT_OUTPUT( \
                (expression), \
                (function), \
                (line) \
            ); \
            for (;;) { \
                OPEN_CFW_EASYLOGGER_ASSERT_WAIT(); \
            } \
        } \
    } while (0)
#endif

#define OPEN_CFW_EASYLOGGER_ASSERT( \
    condition, \
    expression, \
    function, \
    line \
) \
    do { \
        if (!(condition)) { \
            OPEN_CFW_EASYLOGGER_ASSERT_FAILED( \
                (expression), \
                (function), \
                (line) \
            ); \
        } \
    } while (0)

__attribute__((used, noinline))
void open_cfw_easylogger_set_output_enabled(
    open_cfw_easylogger_u8 enabled
)
{
    OPEN_CFW_EASYLOGGER_ASSERT(
        (enabled == 0U) || (enabled == 1U),
        "(enabled == false) || (enabled == true)",
        "elog_set_output_enabled",
        278U
    );
    OPEN_CFW_EASYLOGGER_STATE()->output_enabled = enabled;
}

__attribute__((used, noinline))
void open_cfw_easylogger_set_text_color_enabled(
    open_cfw_easylogger_u8 enabled
)
{
    OPEN_CFW_EASYLOGGER_ASSERT(
        (enabled == 0U) || (enabled == 1U),
        "(enabled == false) || (enabled == true)",
        "elog_set_text_color_enabled",
        290U
    );
    OPEN_CFW_EASYLOGGER_STATE()->text_color_enabled = enabled;
}

__attribute__((used, noinline))
void open_cfw_easylogger_set_format(
    open_cfw_easylogger_u8 level,
    open_cfw_easylogger_u32 format_set
)
{
    OPEN_CFW_EASYLOGGER_ASSERT(
        level <= OPEN_CFW_EASYLOGGER_LEVEL_VERBOSE,
        "level <= ELOG_LVL_VERBOSE",
        "elog_set_fmt",
        321U
    );
    OPEN_CFW_EASYLOGGER_STATE()->enabled_format_set[level] = format_set;
}

__attribute__((used, noinline))
void open_cfw_easylogger_set_filter_level(
    open_cfw_easylogger_u8 level
)
{
    OPEN_CFW_EASYLOGGER_ASSERT(
        level <= OPEN_CFW_EASYLOGGER_LEVEL_VERBOSE,
        "level <= ELOG_LVL_VERBOSE",
        "elog_set_filter_lvl",
        347U
    );
    OPEN_CFW_EASYLOGGER_STATE()->filter.level = level;
}

__attribute__((used, noinline))
void open_cfw_easylogger_set_filter_tag(const char *tag)
{
    (void)OPEN_CFW_EASYLOGGER_FILTER_COPY(
        OPEN_CFW_EASYLOGGER_STATE()->filter.tag,
        tag,
        OPEN_CFW_EASYLOGGER_FILTER_TAG_MAX
    );
}

__attribute__((used, noinline))
void open_cfw_easylogger_output_lock(void)
{
    struct open_cfw_easylogger *logger = OPEN_CFW_EASYLOGGER_STATE();

    if (logger->output_lock_enabled != 0U) {
        OPEN_CFW_EASYLOGGER_PORT_LOCK();
        logger->output_is_locked_before_disable = 1U;
    } else {
        logger->output_is_locked_before_enable = 1U;
    }
}

__attribute__((used, noinline))
void open_cfw_easylogger_output_unlock(void)
{
    struct open_cfw_easylogger *logger = OPEN_CFW_EASYLOGGER_STATE();

    if (logger->output_lock_enabled != 0U) {
        OPEN_CFW_EASYLOGGER_PORT_UNLOCK();
        logger->output_is_locked_before_disable = 0U;
    } else {
        logger->output_is_locked_before_enable = 0U;
    }
}

__attribute__((used, noinline))
void open_cfw_easylogger_output_lock_enabled(
    open_cfw_easylogger_u8 enabled
)
{
    struct open_cfw_easylogger *logger = OPEN_CFW_EASYLOGGER_STATE();

    logger->output_lock_enabled = enabled;
    if (logger->output_lock_enabled != 0U) {
        if (
            (logger->output_is_locked_before_disable == 0U) &&
            (logger->output_is_locked_before_enable != 0U)
        ) {
            OPEN_CFW_EASYLOGGER_PORT_LOCK();
        } else if (
            (logger->output_is_locked_before_disable != 0U) &&
            (logger->output_is_locked_before_enable == 0U)
        ) {
            OPEN_CFW_EASYLOGGER_PORT_UNLOCK();
        }
    }
}
