/*
 * SPDX-License-Identifier: MIT
 *
 * Apollo-main ABI and retained-port seams for the production G2 EasyLogger
 * elog_output source replacement.  The candidate filename is retained so
 * audit links and authenticated source history remain stable.
 */

#ifndef OPEN_CFW_RUNTIME_EASYLOGGER_OUTPUT_CANDIDATE_H
#define OPEN_CFW_RUNTIME_EASYLOGGER_OUTPUT_CANDIDATE_H

typedef __UINT8_TYPE__ open_cfw_easylogger_output_u8;
typedef __UINT32_TYPE__ open_cfw_easylogger_output_u32;
typedef __UINTPTR_TYPE__ open_cfw_easylogger_output_uintptr;
typedef __builtin_va_list open_cfw_easylogger_output_va_list;

enum {
    OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_ASSERT = 0,
    OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_ERROR = 1,
    OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_WARN = 2,
    OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_INFO = 3,
    OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_DEBUG = 4,
    OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_VERBOSE = 5,
    OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_COUNT = 6,
    OPEN_CFW_EASYLOGGER_OUTPUT_LINE_BUFFER_SIZE = 1024,
    OPEN_CFW_EASYLOGGER_OUTPUT_LINE_NUMBER_MAX = 5,
    OPEN_CFW_EASYLOGGER_OUTPUT_TAG_MAX = 30,
    OPEN_CFW_EASYLOGGER_OUTPUT_KEYWORD_MAX = 16,
    OPEN_CFW_EASYLOGGER_OUTPUT_TAG_LEVEL_COUNT = 5,
    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_LEVEL = 0x01,
    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_TAG = 0x02,
    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_TIME = 0x04,
    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_PROCESS = 0x08,
    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_THREAD = 0x10,
    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_DIRECTORY = 0x20,
    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_FUNCTION = 0x40,
    OPEN_CFW_EASYLOGGER_OUTPUT_FMT_LINE = 0x80,
    OPEN_CFW_EASYLOGGER_OUTPUT_LOGGER_ADDRESS = 0x20070BE8U,
    OPEN_CFW_EASYLOGGER_OUTPUT_BUFFER_ADDRESS = 0x2006BD30U,
    OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_HOOK_ADDRESS = 0x2007456CU,
    OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_WAIT_ADDRESS = 0x0044B0AEU,
    OPEN_CFW_EASYLOGGER_OUTPUT_TIME_ADDRESS = 0x0044AAA8U,
    OPEN_CFW_EASYLOGGER_OUTPUT_PROCESS_ADDRESS = 0x0044AB14U,
    OPEN_CFW_EASYLOGGER_OUTPUT_THREAD_ADDRESS = 0x0044AB1CU,
    OPEN_CFW_EASYLOGGER_OUTPUT_SNPRINTF_ADDRESS = 0x0044B728U,
    OPEN_CFW_EASYLOGGER_OUTPUT_VSNPRINTF_ADDRESS = 0x0044B76CU,
    OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_LINE = 572
};

struct open_cfw_easylogger_output_tag_level {
    open_cfw_easylogger_output_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_OUTPUT_TAG_MAX + 1];
    open_cfw_easylogger_output_u8 tag_use_flag;
};

struct open_cfw_easylogger_output_filter {
    open_cfw_easylogger_output_u8 level;
    char tag[OPEN_CFW_EASYLOGGER_OUTPUT_TAG_MAX + 1];
    char keyword[OPEN_CFW_EASYLOGGER_OUTPUT_KEYWORD_MAX + 1];
    struct open_cfw_easylogger_output_tag_level
        tag_level[OPEN_CFW_EASYLOGGER_OUTPUT_TAG_LEVEL_COUNT];
};

struct open_cfw_easylogger_output_logger {
    struct open_cfw_easylogger_output_filter filter;
    open_cfw_easylogger_output_u32
        enabled_format_set[OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_COUNT];
    open_cfw_easylogger_output_u8 init_ok;
    open_cfw_easylogger_output_u8 output_enabled;
    open_cfw_easylogger_output_u8 output_lock_enabled;
    open_cfw_easylogger_output_u8 output_is_locked_before_enable;
    open_cfw_easylogger_output_u8 output_is_locked_before_disable;
    open_cfw_easylogger_output_u8 text_color_enabled;
};

_Static_assert(
    sizeof(open_cfw_easylogger_output_u32) == 4U,
    "G2 EasyLogger size_t width changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_output_tag_level) == 0x21U,
    "G2 EasyLogger tag-level stride changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_output_filter) == 0xD6U,
    "G2 EasyLogger filter layout changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_output_logger,
        enabled_format_set
    ) == 0xD8U,
    "G2 EasyLogger format-mask offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_output_logger,
        output_enabled
    ) == 0xF1U,
    "G2 EasyLogger output-enabled offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_easylogger_output_logger,
        text_color_enabled
    ) == 0xF5U,
    "G2 EasyLogger text-color offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_easylogger_output_logger) == 0xF8U,
    "G2 EasyLogger object size changed"
);

typedef void (*open_cfw_easylogger_output_assert_hook_fn)(
    const char *expression,
    const char *function,
    open_cfw_easylogger_output_u32 line
);
typedef const char *(*open_cfw_easylogger_output_text_fn)(void);
typedef void (*open_cfw_easylogger_output_wait_fn)(void);
typedef int (*open_cfw_easylogger_output_snprintf_fn)(
    char *buffer,
    open_cfw_easylogger_output_u32 size,
    const char *format,
    ...
);
typedef int (*open_cfw_easylogger_output_vsnprintf_fn)(
    char *buffer,
    open_cfw_easylogger_output_u32 size,
    const char *format,
    open_cfw_easylogger_output_va_list arguments
);

/*
 * The defaults below are the focused-disassembly pins. Host oracles override
 * them before including the candidate translation unit. READ_IPSR carries a
 * memory clobber so no observable argument/state/buffer access can migrate
 * ahead of the G2 exception-context gate.
 */
#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_READ_IPSR
static __inline__ open_cfw_easylogger_output_u32
open_cfw_easylogger_output_read_ipsr(void)
{
    open_cfw_easylogger_output_u32 value;
    __asm__ volatile ("mrs %0, ipsr" : "=r" (value) : : "memory");
    return value;
}
#define OPEN_CFW_EASYLOGGER_OUTPUT_READ_IPSR() \
    open_cfw_easylogger_output_read_ipsr()
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_GET_LOGGER
struct open_cfw_easylogger_helpers_logger;
struct open_cfw_easylogger_helpers_logger *
open_cfw_easylogger_helpers_get_logger(void);
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_LOGGER() \
    ((struct open_cfw_easylogger_output_logger *)(void *) \
        open_cfw_easylogger_helpers_get_logger())
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_GET_BUFFER
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_BUFFER() \
    ((char *)(open_cfw_easylogger_output_uintptr) \
        OPEN_CFW_EASYLOGGER_OUTPUT_BUFFER_ADDRESS)
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_GET_ASSERT_HOOK
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_ASSERT_HOOK() \
    (*(open_cfw_easylogger_output_assert_hook_fn volatile *) \
        (open_cfw_easylogger_output_uintptr) \
            OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_HOOK_ADDRESS)
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_SOURCE_PATH
#define OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_SOURCE_PATH \
    ((const char *)(open_cfw_easylogger_output_uintptr)0x006E3098U)
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_WAIT
#define OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_WAIT() \
    (((open_cfw_easylogger_output_wait_fn) \
        ((open_cfw_easylogger_output_uintptr) \
            OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_WAIT_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_GET_TIME
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_TIME() \
    (((open_cfw_easylogger_output_text_fn) \
        ((open_cfw_easylogger_output_uintptr) \
            OPEN_CFW_EASYLOGGER_OUTPUT_TIME_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_GET_PROCESS
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_PROCESS() \
    (((open_cfw_easylogger_output_text_fn) \
        ((open_cfw_easylogger_output_uintptr) \
            OPEN_CFW_EASYLOGGER_OUTPUT_PROCESS_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_GET_THREAD
#define OPEN_CFW_EASYLOGGER_OUTPUT_GET_THREAD() \
    (((open_cfw_easylogger_output_text_fn) \
        ((open_cfw_easylogger_output_uintptr) \
            OPEN_CFW_EASYLOGGER_OUTPUT_THREAD_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_SNPRINTF
#define OPEN_CFW_EASYLOGGER_OUTPUT_SNPRINTF(buffer, size, format, value) \
    (((open_cfw_easylogger_output_snprintf_fn) \
        ((open_cfw_easylogger_output_uintptr) \
            OPEN_CFW_EASYLOGGER_OUTPUT_SNPRINTF_ADDRESS | 1U))( \
                (buffer), (size), (format), (value) \
            ))
#endif

#ifndef OPEN_CFW_EASYLOGGER_OUTPUT_VSNPRINTF
#define OPEN_CFW_EASYLOGGER_OUTPUT_VSNPRINTF( \
    buffer, size, format, arguments \
) \
    (((open_cfw_easylogger_output_vsnprintf_fn) \
        ((open_cfw_easylogger_output_uintptr) \
            OPEN_CFW_EASYLOGGER_OUTPUT_VSNPRINTF_ADDRESS | 1U))( \
                (buffer), (size), (format), (arguments) \
            ))
#endif

/* Existing production helper seams, deliberately not opaque stock entries. */
extern void open_cfw_easylogger_output_lock(void);
extern void open_cfw_easylogger_output_unlock(void);
extern open_cfw_easylogger_output_u8
open_cfw_easylogger_get_filter_tag_level(const char *tag);
extern open_cfw_easylogger_output_u32 open_cfw_easylogger_strcpy(
    open_cfw_easylogger_output_u32 current_length,
    char *destination,
    const char *source
);
extern open_cfw_easylogger_output_u8 open_cfw_easylogger_get_fmt_enabled(
    open_cfw_easylogger_output_u8 level,
    open_cfw_easylogger_output_u32 format_set
);
extern open_cfw_easylogger_output_u8
open_cfw_easylogger_get_fmt_used_and_enabled_u32(
    open_cfw_easylogger_output_u8 level,
    open_cfw_easylogger_output_u32 format_set,
    open_cfw_easylogger_output_u32 argument
);
extern open_cfw_easylogger_output_u8
open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
    open_cfw_easylogger_output_u8 level,
    open_cfw_easylogger_output_u32 format_set,
    const char *argument
);
/*
 * This distinct level-aware source seam exists in the tree but is not yet
 * registered in the production overlay. Promote it (and its selected record
 * builder policy) with this candidate; never bind the upstream level-first
 * elog_async_output ABI here.
 */
extern void open_cfw_g2_easylogger_async_submit(
    const char *buffer,
    open_cfw_easylogger_output_u32 length,
    open_cfw_easylogger_output_u32 level
);

void open_cfw_easylogger_output(
    open_cfw_easylogger_output_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...
);

#endif
