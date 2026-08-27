/*
 * Copyright (c) 2015-2018, Armink, <armink.ztl@gmail.com>
 * SPDX-License-Identifier: MIT
 *
 * Freestanding source replacement for the authenticated EasyLogger output
 * entry in the Even Realities G2 S200 bootloader.  The ordinary formatting
 * flow is adapted from EasyLogger commit
 * a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24.  The early IPSR gate, absolute
 * port seams, RAM tables, buffer placement, assertion metadata, and
 * level-preserving three-argument sink call are recovered G2 behavior.
 */

#include "../../shared/easylogger/runtime_easylogger_helpers.h"

typedef open_cfw_easylogger_helpers_u8 open_cfw_bootloader_elog_output_u8;
typedef open_cfw_easylogger_helpers_u32 open_cfw_bootloader_elog_output_u32;
typedef open_cfw_easylogger_helpers_uintptr
    open_cfw_bootloader_elog_output_uintptr;

enum {
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LEVEL_VERBOSE = 5U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_BUFFER_SIZE = 1024U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_TAG_HALF = 15U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LINE_TEXT_SIZE = 6U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_LEVEL = 0x01U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_TAG = 0x02U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_TIME = 0x04U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_PROCESS = 0x08U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_THREAD = 0x10U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_DIRECTORY = 0x20U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_FUNCTION = 0x40U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_LINE = 0x80U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ASSERT_LINE = 572U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STATE_ADDRESS = 0x20026700U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_BUFFER_ADDRESS = 0x200258D0U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LEVEL_TABLE_ADDRESS = 0x2000031CU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_COLOR_TABLE_ADDRESS = 0x20000334U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ASSERT_HOOK_ADDRESS = 0x200270E4U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ENTRY_THUMB = 0x004176CFU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_GET_TAG_LEVEL_THUMB = 0x0041760BU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LOCK_THUMB = 0x00417571U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_UNLOCK_THUMB = 0x00417593U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_GET_FMT_THUMB = 0x00417AD5U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_GET_FMT_U32_THUMB = 0x00417B49U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_GET_FMT_PTR_THUMB = 0x00417B63U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRCPY_THUMB = 0x0041B159U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRSTR_THUMB = 0x00415FFBU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SINK_THUMB = 0x0041A693U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_TIME_THUMB = 0x0041A6ABU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_PROCESS_THUMB = 0x0041A6F1U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_THREAD_THUMB = 0x0041A6F9U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_WAIT_THUMB = 0x0041AC8BU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SNPRINTF_THUMB = 0x0041B219U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_VSNPRINTF_THUMB = 0x0041B25DU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_TAG_ADDRESS = 0x0043406CU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CSI_END_ADDRESS = 0x0043407CU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FILE_ADDRESS = 0x00430EC0U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ASSERT_FORMAT_ADDRESS = 0x00432E98U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_EXPRESSION_ADDRESS = 0x004335CCU,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FUNCTION_ADDRESS = 0x00433F44U
};

#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CSI_START "\x1b["
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SPACE " "
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_OPEN_BRACKET "["
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CLOSE_BRACKET_SPACE "] "
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_OPEN_PAREN "("
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_COLON ":"
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LINE_FORMAT "%ld"
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CLOSE_PAREN ")"
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_NEWLINE "\n"
#else
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(address) \
    ((const char *)(open_cfw_bootloader_elog_output_uintptr)(address))
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CSI_START \
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(0x00417AD0U)
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SPACE \
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(0x00417B40U)
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_OPEN_BRACKET \
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(0x00417B44U)
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CLOSE_BRACKET_SPACE \
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(0x00417BB8U)
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_OPEN_PAREN \
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(0x00417BBCU)
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_COLON \
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(0x00417BC0U)
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LINE_FORMAT \
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(0x00417BC4U)
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CLOSE_PAREN \
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(0x00417BC8U)
#define OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_NEWLINE \
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRING(0x00417BD0U)
#endif

typedef void (*open_cfw_bootloader_elog_output_assert_hook_fn)(
    const char *expression,
    const char *function,
    open_cfw_bootloader_elog_output_u32 line);
typedef void (*open_cfw_bootloader_elog_output_entry_fn)(
    open_cfw_bootloader_elog_output_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...);
typedef void (*open_cfw_bootloader_elog_output_sink_fn)(
    const char *buffer,
    open_cfw_bootloader_elog_output_u32 length,
    open_cfw_bootloader_elog_output_u8 level);
typedef open_cfw_bootloader_elog_output_u8
    (*open_cfw_bootloader_elog_output_tag_level_fn)(const char *tag);
typedef open_cfw_bootloader_elog_output_u32
    (*open_cfw_bootloader_elog_output_copy_fn)(
        open_cfw_bootloader_elog_output_u32 length,
        char *destination,
        const char *source);
typedef open_cfw_bootloader_elog_output_u8
    (*open_cfw_bootloader_elog_output_get_fmt_fn)(
        open_cfw_bootloader_elog_output_u8 level,
        open_cfw_bootloader_elog_output_u32 format_set);
typedef open_cfw_bootloader_elog_output_u8
    (*open_cfw_bootloader_elog_output_get_fmt_u32_fn)(
        open_cfw_bootloader_elog_output_u8 level,
        open_cfw_bootloader_elog_output_u32 format_set,
        open_cfw_bootloader_elog_output_u32 argument);
typedef open_cfw_bootloader_elog_output_u8
    (*open_cfw_bootloader_elog_output_get_fmt_ptr_fn)(
        open_cfw_bootloader_elog_output_u8 level,
        open_cfw_bootloader_elog_output_u32 format_set,
        const char *argument);
typedef char *(*open_cfw_bootloader_elog_output_strstr_fn)(
    const char *haystack,
    const char *needle);
typedef const char *(*open_cfw_bootloader_elog_output_info_fn)(void);
typedef int (*open_cfw_bootloader_elog_output_snprintf_fn)(
    char *buffer,
    open_cfw_bootloader_elog_output_u32 size,
    const char *format,
    ...);
typedef int (*open_cfw_bootloader_elog_output_vsnprintf_cursor_fn)(
    char *buffer,
    open_cfw_bootloader_elog_output_u32 size,
    const char *format,
    void *argument_cursor);
typedef void (*open_cfw_bootloader_elog_output_void_fn)(void);

void open_cfw_bootloader_easylogger_output_4176ce(
    open_cfw_bootloader_elog_output_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...);
void open_cfw_bootloader_easylogger_output_lock_417570(void);
void open_cfw_bootloader_easylogger_output_unlock_417592(void);
open_cfw_bootloader_elog_output_u8
open_cfw_bootloader_easylogger_get_filter_tag_lvl_41760a(const char *tag);
char *open_cfw_bootloader_strstr(const char *haystack, const char *needle);

#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
struct open_cfw_easylogger_helpers_logger *
open_cfw_bootloader_easylogger_output_host_get_logger(void);
char *open_cfw_bootloader_easylogger_output_host_get_buffer(void);
open_cfw_bootloader_elog_output_u32
open_cfw_bootloader_easylogger_output_host_get_ipsr(void);
const char *open_cfw_bootloader_easylogger_output_host_get_level_text(
    open_cfw_bootloader_elog_output_u8 level);
const char *open_cfw_bootloader_easylogger_output_host_get_color_text(
    open_cfw_bootloader_elog_output_u8 level);
const char *open_cfw_bootloader_easylogger_output_host_get_time(void);
const char *open_cfw_bootloader_easylogger_output_host_get_process(void);
const char *open_cfw_bootloader_easylogger_output_host_get_thread(void);
char *open_cfw_bootloader_easylogger_output_host_strstr(
    const char *haystack,
    const char *needle);
int open_cfw_bootloader_easylogger_output_host_snprintf_line(
    char *buffer,
    open_cfw_bootloader_elog_output_u32 size,
    long line);
int open_cfw_bootloader_easylogger_output_host_vsnprintf(
    char *buffer,
    open_cfw_bootloader_elog_output_u32 size,
    const char *format,
    __builtin_va_list arguments);
void open_cfw_bootloader_easylogger_output_host_sink(
    const char *buffer,
    open_cfw_bootloader_elog_output_u32 length,
    open_cfw_bootloader_elog_output_u8 level);
void open_cfw_bootloader_easylogger_output_host_assert(
    open_cfw_bootloader_elog_output_u32 line);
#endif

static __attribute__((always_inline)) inline
struct open_cfw_easylogger_helpers_logger *
open_cfw_bootloader_easylogger_output_logger(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_get_logger();
#else
    return (struct open_cfw_easylogger_helpers_logger *)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STATE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline char *
open_cfw_bootloader_easylogger_output_buffer(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_get_buffer();
#else
    return (char *)(open_cfw_bootloader_elog_output_uintptr)
        OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_BUFFER_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_output_u32
open_cfw_bootloader_easylogger_output_ipsr(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_get_ipsr();
#else
    open_cfw_bootloader_elog_output_u32 ipsr;
    __asm__ volatile ("mrs %0, ipsr" : "=r" (ipsr));
    return ipsr;
#endif
}

static __attribute__((always_inline)) inline const char *
open_cfw_bootloader_easylogger_output_level_text(
    open_cfw_bootloader_elog_output_u8 level)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_get_level_text(level);
#else
    return ((const char *const volatile *)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LEVEL_TABLE_ADDRESS)[level];
#endif
}

static __attribute__((always_inline)) inline const char *
open_cfw_bootloader_easylogger_output_color_text(
    open_cfw_bootloader_elog_output_u8 level)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_get_color_text(level);
#else
    return ((const char *const volatile *)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_COLOR_TABLE_ADDRESS)[level];
#endif
}

static __attribute__((always_inline)) inline const char *
open_cfw_bootloader_easylogger_output_time(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_get_time();
#else
    return ((open_cfw_bootloader_elog_output_info_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_TIME_THUMB)();
#endif
}

static __attribute__((always_inline)) inline const char *
open_cfw_bootloader_easylogger_output_process(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_get_process();
#else
    return ((open_cfw_bootloader_elog_output_info_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_PROCESS_THUMB)();
#endif
}

static __attribute__((always_inline)) inline const char *
open_cfw_bootloader_easylogger_output_thread(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_get_thread();
#else
    return ((open_cfw_bootloader_elog_output_info_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_THREAD_THUMB)();
#endif
}

static __attribute__((always_inline)) inline char *
open_cfw_bootloader_easylogger_output_strstr(
    const char *haystack,
    const char *needle)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_strstr(haystack, needle);
#else
    return ((open_cfw_bootloader_elog_output_strstr_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRSTR_THUMB)(haystack, needle);
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_output_u8
open_cfw_bootloader_easylogger_output_tag_level(const char *tag)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_get_filter_tag_lvl_41760a(tag);
#else
    return ((open_cfw_bootloader_elog_output_tag_level_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_GET_TAG_LEVEL_THUMB)(tag);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_output_lock(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    open_cfw_bootloader_easylogger_output_lock_417570();
#else
    ((open_cfw_bootloader_elog_output_void_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LOCK_THUMB)();
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_output_unlock(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    open_cfw_bootloader_easylogger_output_unlock_417592();
#else
    ((open_cfw_bootloader_elog_output_void_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_UNLOCK_THUMB)();
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_output_u32
open_cfw_bootloader_easylogger_output_copy(
    open_cfw_bootloader_elog_output_u32 length,
    char *destination,
    const char *source)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_easylogger_strcpy(length, destination, source);
#else
    return ((open_cfw_bootloader_elog_output_copy_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_STRCPY_THUMB)(
                length, destination, source);
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_output_u8
open_cfw_bootloader_easylogger_output_get_fmt(
    open_cfw_bootloader_elog_output_u8 level,
    open_cfw_bootloader_elog_output_u32 format_set)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_easylogger_get_fmt_enabled(level, format_set);
#else
    return ((open_cfw_bootloader_elog_output_get_fmt_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_GET_FMT_THUMB)(level, format_set);
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_output_u8
open_cfw_bootloader_easylogger_output_get_fmt_u32(
    open_cfw_bootloader_elog_output_u8 level,
    open_cfw_bootloader_elog_output_u32 format_set,
    open_cfw_bootloader_elog_output_u32 argument)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_easylogger_get_fmt_used_and_enabled_u32(
        level, format_set, argument);
#else
    return ((open_cfw_bootloader_elog_output_get_fmt_u32_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_GET_FMT_U32_THUMB)(
                level, format_set, argument);
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_output_u8
open_cfw_bootloader_easylogger_output_get_fmt_ptr(
    open_cfw_bootloader_elog_output_u8 level,
    open_cfw_bootloader_elog_output_u32 format_set,
    const char *argument)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_easylogger_get_fmt_used_and_enabled_ptr(
        level, format_set, argument);
#else
    return ((open_cfw_bootloader_elog_output_get_fmt_ptr_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_GET_FMT_PTR_THUMB)(
                level, format_set, argument);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_output_assert(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    open_cfw_bootloader_easylogger_output_host_assert(
        OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ASSERT_LINE);
#else
    const char *const expression = (const char *)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_EXPRESSION_ADDRESS;
    const char *const function = (const char *)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FUNCTION_ADDRESS;
    open_cfw_bootloader_elog_output_assert_hook_fn hook =
        *(open_cfw_bootloader_elog_output_assert_hook_fn volatile *)
            (open_cfw_bootloader_elog_output_uintptr)
                OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ASSERT_HOOK_ADDRESS;
    if (hook != (open_cfw_bootloader_elog_output_assert_hook_fn)0) {
        hook(expression, function, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ASSERT_LINE);
        return;
    }
    ((open_cfw_bootloader_elog_output_entry_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ENTRY_THUMB)(
                0U,
                (const char *)(open_cfw_bootloader_elog_output_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_TAG_ADDRESS,
                (const char *)(open_cfw_bootloader_elog_output_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FILE_ADDRESS,
                function,
                (long)OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ASSERT_LINE,
                (const char *)(open_cfw_bootloader_elog_output_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ASSERT_FORMAT_ADDRESS,
                expression,
                function,
                (long)OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_ASSERT_LINE);
    for (;;) {
        ((open_cfw_bootloader_elog_output_void_fn)
            (open_cfw_bootloader_elog_output_uintptr)
                OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_WAIT_THUMB)();
    }
#endif
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_output_u32
open_cfw_bootloader_easylogger_output_strlen(const char *text)
{
    open_cfw_bootloader_elog_output_u32 length = 0U;
    while (text[length] != '\0') {
        ++length;
    }
    return length;
}

static __attribute__((always_inline)) inline
open_cfw_bootloader_elog_output_u32
open_cfw_bootloader_easylogger_output_append(
    open_cfw_bootloader_elog_output_u32 length,
    const char *text)
{
    return length + open_cfw_bootloader_easylogger_output_copy(
        length,
        open_cfw_bootloader_easylogger_output_buffer() + length,
        text);
}

static __attribute__((always_inline)) inline int
open_cfw_bootloader_easylogger_output_format_line(
    char *buffer,
    open_cfw_bootloader_elog_output_u32 size,
    long line)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_snprintf_line(
        buffer, size, line);
#else
    return ((open_cfw_bootloader_elog_output_snprintf_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SNPRINTF_THUMB)(
                buffer, size, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LINE_FORMAT,
                line);
#endif
}

static __attribute__((always_inline)) inline int
open_cfw_bootloader_easylogger_output_format_message(
    char *buffer,
    open_cfw_bootloader_elog_output_u32 size,
    const char *format,
    __builtin_va_list arguments)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    return open_cfw_bootloader_easylogger_output_host_vsnprintf(
        buffer, size, format, arguments);
#else
    return ((open_cfw_bootloader_elog_output_vsnprintf_cursor_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_VSNPRINTF_THUMB)(
                buffer, size, format, arguments.__ap);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_output_sink(
    const char *buffer,
    open_cfw_bootloader_elog_output_u32 length,
    open_cfw_bootloader_elog_output_u8 level)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
    open_cfw_bootloader_easylogger_output_host_sink(buffer, length, level);
#else
    ((open_cfw_bootloader_elog_output_sink_fn)
        (open_cfw_bootloader_elog_output_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SINK_THUMB)(buffer, length, level);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_output_4176ce(
    open_cfw_bootloader_elog_output_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...)
{
    struct open_cfw_easylogger_helpers_logger *logger;
    open_cfw_bootloader_elog_output_u32 tag_length;
    char line_text[OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LINE_TEXT_SIZE];
    char tag_space[OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_TAG_HALF + 1U];
    __builtin_va_list arguments;
    open_cfw_bootloader_elog_output_u32 length = 0U;
    int format_result;

    if (open_cfw_bootloader_easylogger_output_ipsr() != 0U) {
        return;
    }
    logger = open_cfw_bootloader_easylogger_output_logger();
    if (level > OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LEVEL_VERBOSE) {
        open_cfw_bootloader_easylogger_output_assert();
    }
    if (logger->output_enabled == 0U || level > logger->filter.level ||
            level >
                open_cfw_bootloader_easylogger_output_tag_level(tag) ||
            open_cfw_bootloader_easylogger_output_strstr(
                tag, logger->filter.tag) == (char *)0) {
        return;
    }

    tag_length = open_cfw_bootloader_easylogger_output_strlen(tag);
    {
        open_cfw_bootloader_elog_output_u32 index;
        for (index = 0U;
                index < OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LINE_TEXT_SIZE;
                ++index) {
            line_text[index] = '\0';
        }
        for (index = 0U;
                index < OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_TAG_HALF + 1U;
                ++index) {
            tag_space[index] = '\0';
        }
    }

    __builtin_va_start(arguments, format);
    open_cfw_bootloader_easylogger_output_lock();

    if (logger->text_color_enabled != 0U) {
        length = open_cfw_bootloader_easylogger_output_append(
            length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CSI_START);
        length = open_cfw_bootloader_easylogger_output_append(
            length, open_cfw_bootloader_easylogger_output_color_text(level));
    }
    if (open_cfw_bootloader_easylogger_output_get_fmt(
            level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_LEVEL) != 0U) {
        length = open_cfw_bootloader_easylogger_output_append(
            length, open_cfw_bootloader_easylogger_output_level_text(level));
    }
    if (open_cfw_bootloader_easylogger_output_get_fmt(
            level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_TAG) != 0U) {
        open_cfw_bootloader_elog_output_u32 index;
        length = open_cfw_bootloader_easylogger_output_append(length, tag);
        if (tag_length <= OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_TAG_HALF) {
            for (index = 0U;
                    index < OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_TAG_HALF - tag_length;
                    ++index) {
                tag_space[index] = ' ';
            }
            length = open_cfw_bootloader_easylogger_output_append(
                length, tag_space);
        }
        length = open_cfw_bootloader_easylogger_output_append(
            length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SPACE);
    }

    if (open_cfw_bootloader_easylogger_output_get_fmt(
            level,
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_TIME |
                OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_PROCESS |
                OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_THREAD) != 0U) {
        length = open_cfw_bootloader_easylogger_output_append(
            length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_OPEN_BRACKET);
        if (open_cfw_bootloader_easylogger_output_get_fmt(
                level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_TIME) != 0U) {
            length = open_cfw_bootloader_easylogger_output_append(
                length, open_cfw_bootloader_easylogger_output_time());
            if (open_cfw_bootloader_easylogger_output_get_fmt(
                    level,
                    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_PROCESS |
                        OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_THREAD) != 0U) {
                length = open_cfw_bootloader_easylogger_output_append(
                    length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SPACE);
            }
        }
        if (open_cfw_bootloader_easylogger_output_get_fmt(
                level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_PROCESS) != 0U) {
            length = open_cfw_bootloader_easylogger_output_append(
                length, open_cfw_bootloader_easylogger_output_process());
            if (open_cfw_bootloader_easylogger_output_get_fmt(
                    level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_THREAD) != 0U) {
                length = open_cfw_bootloader_easylogger_output_append(
                    length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SPACE);
            }
        }
        if (open_cfw_bootloader_easylogger_output_get_fmt(
                level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_THREAD) != 0U) {
            length = open_cfw_bootloader_easylogger_output_append(
                length, open_cfw_bootloader_easylogger_output_thread());
        }
        length = open_cfw_bootloader_easylogger_output_append(
            length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CLOSE_BRACKET_SPACE);
    }

    if (open_cfw_bootloader_easylogger_output_get_fmt_ptr(
                level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_DIRECTORY, file) !=
            0U ||
            open_cfw_bootloader_easylogger_output_get_fmt_ptr(
                level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_FUNCTION,
                function) != 0U ||
            open_cfw_bootloader_easylogger_output_get_fmt_u32(
                level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_LINE,
                (open_cfw_bootloader_elog_output_u32)line) != 0U) {
        length = open_cfw_bootloader_easylogger_output_append(
            length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_OPEN_PAREN);
        if (open_cfw_bootloader_easylogger_output_get_fmt_ptr(
                level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_DIRECTORY, file) !=
                0U) {
            length = open_cfw_bootloader_easylogger_output_append(length, file);
            if (open_cfw_bootloader_easylogger_output_get_fmt_ptr(
                    level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_FUNCTION,
                    function) != 0U) {
                length = open_cfw_bootloader_easylogger_output_append(
                    length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_COLON);
            } else if (open_cfw_bootloader_easylogger_output_get_fmt_u32(
                    level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_LINE,
                    (open_cfw_bootloader_elog_output_u32)line) != 0U) {
                length = open_cfw_bootloader_easylogger_output_append(
                    length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SPACE);
            }
        }
        if (open_cfw_bootloader_easylogger_output_get_fmt_u32(
                level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_LINE,
                (open_cfw_bootloader_elog_output_u32)line) != 0U) {
            (void)open_cfw_bootloader_easylogger_output_format_line(
                line_text, 5U, line);
            length = open_cfw_bootloader_easylogger_output_append(
                length, line_text);
            if (open_cfw_bootloader_easylogger_output_get_fmt_ptr(
                    level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_FUNCTION,
                    function) != 0U) {
                length = open_cfw_bootloader_easylogger_output_append(
                    length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_SPACE);
            }
        }
        if (open_cfw_bootloader_easylogger_output_get_fmt_ptr(
                level, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_FMT_FUNCTION,
                function) != 0U) {
            length = open_cfw_bootloader_easylogger_output_append(
                length, function);
        }
        length = open_cfw_bootloader_easylogger_output_append(
            length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CLOSE_PAREN);
    }

    format_result = open_cfw_bootloader_easylogger_output_format_message(
        open_cfw_bootloader_easylogger_output_buffer() + length,
        OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_BUFFER_SIZE - length,
        format,
        arguments);
    __builtin_va_end(arguments);
    if (format_result > -1 &&
            length + (open_cfw_bootloader_elog_output_u32)format_result <=
                OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_BUFFER_SIZE) {
        length += (open_cfw_bootloader_elog_output_u32)format_result;
    } else {
        length = OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_BUFFER_SIZE;
    }

    if (length + 4U + 1U > OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_BUFFER_SIZE) {
        length = OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_BUFFER_SIZE - 4U - 1U;
    }
    if (logger->filter.keyword[0] != '\0') {
        open_cfw_bootloader_easylogger_output_buffer()[length] = '\0';
        if (open_cfw_bootloader_easylogger_output_strstr(
                open_cfw_bootloader_easylogger_output_buffer(),
                logger->filter.keyword) == (char *)0) {
            open_cfw_bootloader_easylogger_output_unlock();
            return;
        }
    }
    if (logger->text_color_enabled != 0U) {
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST)
        length = open_cfw_bootloader_easylogger_output_append(
            length, "\x1b[0m");
#else
        length = open_cfw_bootloader_easylogger_output_append(
            length,
            (const char *)(open_cfw_bootloader_elog_output_uintptr)
                OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_CSI_END_ADDRESS);
#endif
    }
    length = open_cfw_bootloader_easylogger_output_append(
        length, OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_NEWLINE);
    open_cfw_bootloader_easylogger_output_sink(
        open_cfw_bootloader_easylogger_output_buffer(), length, level);
    open_cfw_bootloader_easylogger_output_unlock();
}
