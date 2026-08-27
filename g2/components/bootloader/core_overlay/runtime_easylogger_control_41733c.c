/*
 * Copyright (c) 2015-2018, Armink, <armink.ztl@gmail.com>
 * SPDX-License-Identifier: MIT
 *
 * Bounded freestanding adaptation of the authenticated EasyLogger control,
 * lock, and tag-level query entries in the Even Realities G2 S200 bootloader.
 */

#include "../../shared/easylogger/runtime_easylogger_helpers.h"

typedef open_cfw_easylogger_helpers_u8 open_cfw_bootloader_elog_u8;
typedef open_cfw_easylogger_helpers_u32 open_cfw_bootloader_elog_u32;
typedef open_cfw_easylogger_helpers_uintptr open_cfw_bootloader_elog_uintptr;

enum {
    OPEN_CFW_BOOTLOADER_ELOG_LEVEL_INFO = 3U,
    OPEN_CFW_BOOTLOADER_ELOG_LEVEL_VERBOSE = 5U,
    OPEN_CFW_BOOTLOADER_ELOG_TAG_LEVEL_COUNT = 5U,
    OPEN_CFW_BOOTLOADER_ELOG_TAG_MAX = 30U,
    OPEN_CFW_BOOTLOADER_ELOG_PORT_INIT_THUMB = 0x0041A685U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LOCK_ENABLED_THUMB = 0x00417B7DU,
    OPEN_CFW_BOOTLOADER_ELOG_PORT_LOCK_THUMB = 0x0041A69BU,
    OPEN_CFW_BOOTLOADER_ELOG_PORT_UNLOCK_THUMB = 0x0041A6A3U,
    OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_THUMB = 0x004176CFU,
    OPEN_CFW_BOOTLOADER_ELOG_WAIT_THUMB = 0x0041AC8BU,
    OPEN_CFW_BOOTLOADER_ELOG_STRNCMP_THUMB = 0x0041B0F5U,
    OPEN_CFW_BOOTLOADER_ELOG_ASSERT_HOOK_ADDRESS = 0x200270E4U,
    OPEN_CFW_BOOTLOADER_ELOG_TAG_ADDRESS = 0x0043406CU,
    OPEN_CFW_BOOTLOADER_ELOG_FILE_ADDRESS = 0x00430EC0U,
    OPEN_CFW_BOOTLOADER_ELOG_ASSERT_FORMAT_ADDRESS = 0x00432E98U,
    OPEN_CFW_BOOTLOADER_ELOG_START_FUNCTION_ADDRESS = 0x00433F38U,
    OPEN_CFW_BOOTLOADER_ELOG_START_FORMAT_ADDRESS = 0x00432AC4U,
    OPEN_CFW_BOOTLOADER_ELOG_VERSION_ADDRESS = 0x00434074U,
    OPEN_CFW_BOOTLOADER_ELOG_BOOL_EXPRESSION_ADDRESS = 0x00432AECU,
    OPEN_CFW_BOOTLOADER_ELOG_LEVEL_EXPRESSION_ADDRESS = 0x004335CCU,
    OPEN_CFW_BOOTLOADER_ELOG_TAG_EXPRESSION_ADDRESS = 0x00433B28U,
    OPEN_CFW_BOOTLOADER_ELOG_SET_OUTPUT_FUNCTION_ADDRESS = 0x00433874U,
    OPEN_CFW_BOOTLOADER_ELOG_SET_COLOR_FUNCTION_ADDRESS = 0x004335B0U,
    OPEN_CFW_BOOTLOADER_ELOG_SET_FMT_FUNCTION_ADDRESS = 0x00433D08U,
    OPEN_CFW_BOOTLOADER_ELOG_SET_FILTER_FUNCTION_ADDRESS = 0x00433B14U,
    OPEN_CFW_BOOTLOADER_ELOG_GET_TAG_LEVEL_FUNCTION_ADDRESS = 0x0043388CU,
    OPEN_CFW_BOOTLOADER_ELOG_SET_OUTPUT_LINE = 278U,
    OPEN_CFW_BOOTLOADER_ELOG_SET_COLOR_LINE = 290U,
    OPEN_CFW_BOOTLOADER_ELOG_SET_FMT_LINE = 321U,
    OPEN_CFW_BOOTLOADER_ELOG_SET_FILTER_LINE = 347U,
    OPEN_CFW_BOOTLOADER_ELOG_GET_TAG_LEVEL_LINE = 481U,
    OPEN_CFW_BOOTLOADER_ELOG_START_LINE = 247U
};

typedef open_cfw_bootloader_elog_u8 (*open_cfw_bootloader_elog_port_init_fn)(
    void);
typedef void (*open_cfw_bootloader_elog_bool_fn)(
    open_cfw_bootloader_elog_u8 value);
typedef void (*open_cfw_bootloader_elog_void_fn)(void);
typedef int (*open_cfw_bootloader_elog_strncmp_fn)(
    const char *left,
    const char *right,
    open_cfw_bootloader_elog_u32 count);
typedef void (*open_cfw_bootloader_elog_assert_hook_fn)(
    const char *expression,
    const char *function,
    open_cfw_bootloader_elog_u32 line);
typedef void (*open_cfw_bootloader_elog_output_fn)(
    open_cfw_bootloader_elog_u8 level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...);

#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST)
struct open_cfw_easylogger_helpers_logger *
open_cfw_bootloader_easylogger_host_get_logger(void);
open_cfw_bootloader_elog_u8
open_cfw_bootloader_easylogger_host_port_init(void);
void open_cfw_bootloader_easylogger_host_output_lock_enabled(
    open_cfw_bootloader_elog_u8 enabled);
void open_cfw_bootloader_easylogger_host_port_lock(void);
void open_cfw_bootloader_easylogger_host_port_unlock(void);
void open_cfw_bootloader_easylogger_host_assert(
    open_cfw_bootloader_elog_u32 line);
void open_cfw_bootloader_easylogger_host_start_output(void);
int open_cfw_bootloader_easylogger_host_strncmp(
    const char *left,
    const char *right,
    open_cfw_bootloader_elog_u32 count);
#endif

static __attribute__((always_inline)) inline
struct open_cfw_easylogger_helpers_logger *
open_cfw_bootloader_easylogger_logger(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST)
    return open_cfw_bootloader_easylogger_host_get_logger();
#else
    return (struct open_cfw_easylogger_helpers_logger *)
        (open_cfw_bootloader_elog_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_STATE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline open_cfw_bootloader_elog_u32
open_cfw_bootloader_easylogger_expression_address(
    open_cfw_bootloader_elog_u32 line)
{
    if (line == OPEN_CFW_BOOTLOADER_ELOG_SET_OUTPUT_LINE ||
            line == OPEN_CFW_BOOTLOADER_ELOG_SET_COLOR_LINE) {
        return OPEN_CFW_BOOTLOADER_ELOG_BOOL_EXPRESSION_ADDRESS;
    }
    if (line == OPEN_CFW_BOOTLOADER_ELOG_GET_TAG_LEVEL_LINE) {
        return OPEN_CFW_BOOTLOADER_ELOG_TAG_EXPRESSION_ADDRESS;
    }
    return OPEN_CFW_BOOTLOADER_ELOG_LEVEL_EXPRESSION_ADDRESS;
}

static __attribute__((always_inline)) inline open_cfw_bootloader_elog_u32
open_cfw_bootloader_easylogger_function_address(
    open_cfw_bootloader_elog_u32 line)
{
    switch (line) {
    case OPEN_CFW_BOOTLOADER_ELOG_SET_OUTPUT_LINE:
        return OPEN_CFW_BOOTLOADER_ELOG_SET_OUTPUT_FUNCTION_ADDRESS;
    case OPEN_CFW_BOOTLOADER_ELOG_SET_COLOR_LINE:
        return OPEN_CFW_BOOTLOADER_ELOG_SET_COLOR_FUNCTION_ADDRESS;
    case OPEN_CFW_BOOTLOADER_ELOG_SET_FMT_LINE:
        return OPEN_CFW_BOOTLOADER_ELOG_SET_FMT_FUNCTION_ADDRESS;
    case OPEN_CFW_BOOTLOADER_ELOG_SET_FILTER_LINE:
        return OPEN_CFW_BOOTLOADER_ELOG_SET_FILTER_FUNCTION_ADDRESS;
    default:
        return OPEN_CFW_BOOTLOADER_ELOG_GET_TAG_LEVEL_FUNCTION_ADDRESS;
    }
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_require(
    int condition,
    open_cfw_bootloader_elog_u32 line)
{
    if (!condition) {
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST)
        open_cfw_bootloader_easylogger_host_assert(line);
#else
        const char *const expression = (const char *)
            (open_cfw_bootloader_elog_uintptr)
                open_cfw_bootloader_easylogger_expression_address(line);
        const char *const function = (const char *)
            (open_cfw_bootloader_elog_uintptr)
                open_cfw_bootloader_easylogger_function_address(line);
        open_cfw_bootloader_elog_assert_hook_fn hook =
            *(open_cfw_bootloader_elog_assert_hook_fn volatile *)
                (open_cfw_bootloader_elog_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_ASSERT_HOOK_ADDRESS;
        if (hook != (open_cfw_bootloader_elog_assert_hook_fn)0) {
            hook(expression, function, line);
            return;
        }
        ((open_cfw_bootloader_elog_output_fn)
            (open_cfw_bootloader_elog_uintptr)
                OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_THUMB)(
                    0U,
                    (const char *)(open_cfw_bootloader_elog_uintptr)
                        OPEN_CFW_BOOTLOADER_ELOG_TAG_ADDRESS,
                    (const char *)(open_cfw_bootloader_elog_uintptr)
                        OPEN_CFW_BOOTLOADER_ELOG_FILE_ADDRESS,
                    function,
                    (long)line,
                    (const char *)(open_cfw_bootloader_elog_uintptr)
                        OPEN_CFW_BOOTLOADER_ELOG_ASSERT_FORMAT_ADDRESS,
                    expression,
                    function,
                    (long)line);
        for (;;) {
            ((open_cfw_bootloader_elog_void_fn)
                (open_cfw_bootloader_elog_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_WAIT_THUMB)();
        }
#endif
    }
}

void open_cfw_bootloader_easylogger_set_output_enabled_4173ca(
    open_cfw_bootloader_elog_u8 enabled);
void open_cfw_bootloader_easylogger_set_text_color_enabled_417438(
    open_cfw_bootloader_elog_u8 enabled);
void open_cfw_bootloader_easylogger_set_filter_lvl_417510(
    open_cfw_bootloader_elog_u8 level);
void open_cfw_bootloader_easylogger_filter_tag_lvl_default_4175b4(void);
void open_cfw_bootloader_easylogger_output_lock_417570(void);
void open_cfw_bootloader_easylogger_output_unlock_417592(void);

__attribute__((used, noinline))
open_cfw_bootloader_elog_u8 open_cfw_bootloader_easylogger_init_41733c(void)
{
    struct open_cfw_easylogger_helpers_logger *const logger =
        open_cfw_bootloader_easylogger_logger();
    open_cfw_bootloader_elog_u8 result = 0U;

    if (logger->init_ok == 1U) {
        return result;
    }
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST)
    result = open_cfw_bootloader_easylogger_host_port_init();
#else
    result = ((open_cfw_bootloader_elog_port_init_fn)
        (open_cfw_bootloader_elog_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_PORT_INIT_THUMB)();
#endif
    if (result != 0U) {
        return result;
    }
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST)
    open_cfw_bootloader_easylogger_host_output_lock_enabled(1U);
#else
    ((open_cfw_bootloader_elog_bool_fn)
        (open_cfw_bootloader_elog_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_LOCK_ENABLED_THUMB)(1U);
#endif
    logger->output_is_locked_before_enable = 0U;
    logger->output_is_locked_before_disable = 0U;
    open_cfw_bootloader_easylogger_set_text_color_enabled_417438(1U);
    open_cfw_bootloader_easylogger_set_filter_lvl_417510(
        OPEN_CFW_BOOTLOADER_ELOG_LEVEL_VERBOSE);
    open_cfw_bootloader_easylogger_filter_tag_lvl_default_4175b4();
    logger->init_ok = 1U;
    return result;
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_start_417392(void)
{
    if (open_cfw_bootloader_easylogger_logger()->init_ok == 0U) {
        return;
    }
    open_cfw_bootloader_easylogger_set_output_enabled_4173ca(1U);
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST)
    open_cfw_bootloader_easylogger_host_start_output();
#else
    ((open_cfw_bootloader_elog_output_fn)
        (open_cfw_bootloader_elog_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_OUTPUT_THUMB)(
                OPEN_CFW_BOOTLOADER_ELOG_LEVEL_INFO,
                (const char *)(open_cfw_bootloader_elog_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_TAG_ADDRESS,
                (const char *)(open_cfw_bootloader_elog_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_FILE_ADDRESS,
                (const char *)(open_cfw_bootloader_elog_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_START_FUNCTION_ADDRESS,
                (long)OPEN_CFW_BOOTLOADER_ELOG_START_LINE,
                (const char *)(open_cfw_bootloader_elog_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_START_FORMAT_ADDRESS,
                (const char *)(open_cfw_bootloader_elog_uintptr)
                    OPEN_CFW_BOOTLOADER_ELOG_VERSION_ADDRESS);
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_set_output_enabled_4173ca(
    open_cfw_bootloader_elog_u8 enabled)
{
    open_cfw_bootloader_easylogger_require(enabled <= 1U,
        OPEN_CFW_BOOTLOADER_ELOG_SET_OUTPUT_LINE);
    open_cfw_bootloader_easylogger_logger()->output_enabled = enabled;
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_set_text_color_enabled_417438(
    open_cfw_bootloader_elog_u8 enabled)
{
    open_cfw_bootloader_easylogger_require(enabled <= 1U,
        OPEN_CFW_BOOTLOADER_ELOG_SET_COLOR_LINE);
    open_cfw_bootloader_easylogger_logger()->text_color_enabled = enabled;
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_set_fmt_4174a6(
    open_cfw_bootloader_elog_u8 level,
    open_cfw_bootloader_elog_u32 format_set)
{
    open_cfw_bootloader_easylogger_require(
        level <= OPEN_CFW_BOOTLOADER_ELOG_LEVEL_VERBOSE,
        OPEN_CFW_BOOTLOADER_ELOG_SET_FMT_LINE);
    open_cfw_bootloader_easylogger_logger()->enabled_format_set[level] =
        format_set;
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_set_filter_lvl_417510(
    open_cfw_bootloader_elog_u8 level)
{
    open_cfw_bootloader_easylogger_require(
        level <= OPEN_CFW_BOOTLOADER_ELOG_LEVEL_VERBOSE,
        OPEN_CFW_BOOTLOADER_ELOG_SET_FILTER_LINE);
    open_cfw_bootloader_easylogger_logger()->filter.level = level;
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_output_lock_417570(void)
{
    struct open_cfw_easylogger_helpers_logger *const logger =
        open_cfw_bootloader_easylogger_logger();
    if (logger->output_lock_enabled != 0U) {
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST)
        open_cfw_bootloader_easylogger_host_port_lock();
#else
        ((open_cfw_bootloader_elog_void_fn)
            (open_cfw_bootloader_elog_uintptr)
                OPEN_CFW_BOOTLOADER_ELOG_PORT_LOCK_THUMB)();
#endif
        logger->output_is_locked_before_disable = 1U;
    } else {
        logger->output_is_locked_before_enable = 1U;
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_output_unlock_417592(void)
{
    struct open_cfw_easylogger_helpers_logger *const logger =
        open_cfw_bootloader_easylogger_logger();
    if (logger->output_lock_enabled != 0U) {
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST)
        open_cfw_bootloader_easylogger_host_port_unlock();
#else
        ((open_cfw_bootloader_elog_void_fn)
            (open_cfw_bootloader_elog_uintptr)
                OPEN_CFW_BOOTLOADER_ELOG_PORT_UNLOCK_THUMB)();
#endif
        logger->output_is_locked_before_disable = 0U;
    } else {
        logger->output_is_locked_before_enable = 0U;
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_filter_tag_lvl_default_4175b4(void)
{
    struct open_cfw_easylogger_helpers_logger *const logger =
        open_cfw_bootloader_easylogger_logger();
    open_cfw_bootloader_elog_u32 index;
    open_cfw_bootloader_elog_u32 byte;

    for (index = 0U;
         index < OPEN_CFW_BOOTLOADER_ELOG_TAG_LEVEL_COUNT;
         ++index) {
        for (byte = 0U; byte <= OPEN_CFW_BOOTLOADER_ELOG_TAG_MAX; ++byte) {
            logger->filter.tag_level[index].tag[byte] = '\0';
        }
        logger->filter.tag_level[index].level = 0U;
        logger->filter.tag_level[index].tag_use_flag = 0U;
    }
}

__attribute__((used, noinline))
open_cfw_bootloader_elog_u8
open_cfw_bootloader_easylogger_get_filter_tag_lvl_41760a(const char *tag)
{
    struct open_cfw_easylogger_helpers_logger *const logger =
        open_cfw_bootloader_easylogger_logger();
    open_cfw_bootloader_elog_u8 level =
        OPEN_CFW_BOOTLOADER_ELOG_LEVEL_VERBOSE;
    open_cfw_bootloader_elog_u32 index;

    open_cfw_bootloader_easylogger_require(tag != (const char *)0,
        OPEN_CFW_BOOTLOADER_ELOG_GET_TAG_LEVEL_LINE);
    if (logger->init_ok == 0U) {
        return level;
    }
    open_cfw_bootloader_easylogger_output_lock_417570();
    for (index = 0U;
         index < OPEN_CFW_BOOTLOADER_ELOG_TAG_LEVEL_COUNT;
         ++index) {
        int comparison;
        if (logger->filter.tag_level[index].tag_use_flag != 1U) {
            continue;
        }
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST)
        comparison = open_cfw_bootloader_easylogger_host_strncmp(
            tag,
            logger->filter.tag_level[index].tag,
            OPEN_CFW_BOOTLOADER_ELOG_TAG_MAX);
#else
        comparison = ((open_cfw_bootloader_elog_strncmp_fn)
            (open_cfw_bootloader_elog_uintptr)
                OPEN_CFW_BOOTLOADER_ELOG_STRNCMP_THUMB)(
                    tag,
                    logger->filter.tag_level[index].tag,
                    OPEN_CFW_BOOTLOADER_ELOG_TAG_MAX);
#endif
        if (comparison == 0) {
            level = logger->filter.tag_level[index].level;
            break;
        }
    }
    open_cfw_bootloader_easylogger_output_unlock_417592();
    return level;
}
