#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE \
    OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER
#include "../../components/shared/easylogger/runtime_easylogger_helpers.h"

static struct open_cfw_easylogger_helpers_logger logger_state;
static char line_buffer[OPEN_CFW_EASYLOGGER_HELPERS_LINE_BUFFER_SIZE];
static char captured[OPEN_CFW_EASYLOGGER_HELPERS_LINE_BUFFER_SIZE + 1U];
static const char *const level_text[6] = {
    "A/", "E/", "W/", "I/", "D/", "V/"
};
static const char *const color_text[6] = {
    "35;22m", "31;22m", "33;22m", "36;22m", "32;22m", "34;22m"
};
static uint32_t ipsr_value;
static unsigned lock_calls;
static unsigned unlock_calls;
static unsigned sink_calls;
static unsigned helper_assert_calls;
static unsigned output_assert_calls;
static uint32_t captured_length;
static uint8_t captured_level;

struct open_cfw_easylogger_helpers_logger *
open_cfw_easylogger_helpers_get_logger(void)
{
    return &logger_state;
}

void open_cfw_easylogger_helpers_assert_failed(uint32_t line)
{
    (void)line;
    ++helper_assert_calls;
}

#include "../../components/shared/easylogger/runtime_easylogger_helpers.c"

#define OPEN_CFW_BOOTLOADER_EASYLOGGER_OUTPUT_HOST 1
#include "../../components/bootloader/core_overlay/runtime_easylogger_output_4176ce.c"

static void reset_state(void)
{
    memset(&logger_state, 0, sizeof(logger_state));
    memset(line_buffer, 0xA5, sizeof(line_buffer));
    memset(captured, 0, sizeof(captured));
    ipsr_value = 0U;
    lock_calls = 0U;
    unlock_calls = 0U;
    sink_calls = 0U;
    helper_assert_calls = 0U;
    output_assert_calls = 0U;
    captured_length = 0U;
    captured_level = 0U;
}

static void enable_logger(uint32_t format_mask)
{
    unsigned level;
    logger_state.init_ok = 1U;
    logger_state.output_enabled = 1U;
    logger_state.output_lock_enabled = 1U;
    logger_state.filter.level = 5U;
    for (level = 0U; level < 6U; ++level) {
        logger_state.enabled_format_set[level] = format_mask;
    }
}

struct open_cfw_easylogger_helpers_logger *
open_cfw_bootloader_easylogger_output_host_get_logger(void)
{
    return &logger_state;
}

char *open_cfw_bootloader_easylogger_output_host_get_buffer(void)
{
    return line_buffer;
}

uint32_t open_cfw_bootloader_easylogger_output_host_get_ipsr(void)
{
    return ipsr_value;
}

const char *open_cfw_bootloader_easylogger_output_host_get_level_text(
    uint8_t level)
{
    return level_text[level];
}

const char *open_cfw_bootloader_easylogger_output_host_get_color_text(
    uint8_t level)
{
    return color_text[level];
}

const char *open_cfw_bootloader_easylogger_output_host_get_time(void)
{
    return "123";
}

const char *open_cfw_bootloader_easylogger_output_host_get_process(void)
{
    return "proc";
}

const char *open_cfw_bootloader_easylogger_output_host_get_thread(void)
{
    return "task";
}

char *open_cfw_bootloader_easylogger_output_host_strstr(
    const char *haystack,
    const char *needle)
{
    return strstr(haystack, needle);
}

int open_cfw_bootloader_easylogger_output_host_snprintf_line(
    char *buffer,
    uint32_t size,
    long line)
{
    return snprintf(buffer, size, "%ld", line);
}

int open_cfw_bootloader_easylogger_output_host_vsnprintf(
    char *buffer,
    uint32_t size,
    const char *format,
    __builtin_va_list arguments)
{
    return vsnprintf(buffer, size, format, arguments);
}

void open_cfw_bootloader_easylogger_output_host_sink(
    const char *buffer,
    uint32_t length,
    uint8_t level)
{
    ++sink_calls;
    captured_length = length;
    captured_level = level;
    memcpy(captured, buffer, length);
    captured[length] = '\0';
}

void open_cfw_bootloader_easylogger_output_host_assert(uint32_t line)
{
    if (line == 572U) {
        ++output_assert_calls;
    }
}

void open_cfw_bootloader_easylogger_output_lock_417570(void)
{
    ++lock_calls;
}

void open_cfw_bootloader_easylogger_output_unlock_417592(void)
{
    ++unlock_calls;
}

uint8_t open_cfw_bootloader_easylogger_get_filter_tag_lvl_41760a(
    const char *tag)
{
    unsigned slot;
    uint8_t result = 5U;
    ++lock_calls;
    for (slot = 0U; slot < 5U; ++slot) {
        if (logger_state.filter.tag_level[slot].tag_use_flag != 0U &&
                strncmp(
                    tag, logger_state.filter.tag_level[slot].tag,
                    OPEN_CFW_EASYLOGGER_HELPERS_TAG_MAX) == 0) {
            result = logger_state.filter.tag_level[slot].level;
            break;
        }
    }
    ++unlock_calls;
    return result;
}

unsigned open_cfw_test_easylogger_output_interrupt_gate(void)
{
    reset_state();
    ipsr_value = 11U;
    open_cfw_bootloader_easylogger_output_4176ce(
        9U, NULL, NULL, NULL, 0L, NULL);
    return sink_calls == 0U && lock_calls == 0U && unlock_calls == 0U &&
        output_assert_calls == 0U;
}

unsigned open_cfw_test_easylogger_output_plain_and_filters(void)
{
    reset_state();
    enable_logger(0U);
    open_cfw_bootloader_easylogger_output_4176ce(
        3U, "boot", NULL, NULL, 0L, "hello %d", 7);
    if (sink_calls != 1U || captured_level != 3U ||
            strcmp(captured, "hello 7\n") != 0 ||
            lock_calls != 2U || unlock_calls != 2U) {
        return 0U;
    }
    logger_state.output_enabled = 0U;
    open_cfw_bootloader_easylogger_output_4176ce(
        3U, "boot", NULL, NULL, 0L, "disabled");
    if (sink_calls != 1U) {
        return 0U;
    }
    logger_state.output_enabled = 1U;
    logger_state.filter.level = 2U;
    open_cfw_bootloader_easylogger_output_4176ce(
        3U, "boot", NULL, NULL, 0L, "level");
    if (sink_calls != 1U) {
        return 0U;
    }
    logger_state.filter.level = 5U;
    strcpy(logger_state.filter.tag, "wanted");
    open_cfw_bootloader_easylogger_output_4176ce(
        3U, "boot", NULL, NULL, 0L, "tag");
    return sink_calls == 1U;
}

unsigned open_cfw_test_easylogger_output_full_format(void)
{
    static const char expected[] =
        "\x1b[36;22mI/boot            [123 task] (42 fn)value=9\x1b[0m\n";
    reset_state();
    enable_logger(0xD7U);
    logger_state.text_color_enabled = 1U;
    open_cfw_bootloader_easylogger_output_4176ce(
        3U, "boot", "ignored.c", "fn", 42L, "value=%d", 9);
    return sink_calls == 1U && captured_level == 3U &&
        strcmp(captured, expected) == 0 &&
        captured_length == sizeof(expected) - 1U;
}

unsigned open_cfw_test_easylogger_output_directory_process(void)
{
    reset_state();
    enable_logger(0xFCU);
    open_cfw_bootloader_easylogger_output_4176ce(
        2U, "x", "path.c", "worker", 9L, " ok");
    return sink_calls == 1U &&
        strcmp(captured, "[123 proc task] (path.c:9 worker) ok\n") == 0;
}

unsigned open_cfw_test_easylogger_output_keyword(void)
{
    reset_state();
    enable_logger(0U);
    strcpy(logger_state.filter.keyword, "needle");
    open_cfw_bootloader_easylogger_output_4176ce(
        3U, "boot", NULL, NULL, 0L, "no match");
    if (sink_calls != 0U || lock_calls != 2U || unlock_calls != 2U) {
        return 0U;
    }
    open_cfw_bootloader_easylogger_output_4176ce(
        3U, "boot", NULL, NULL, 0L, "has needle here");
    return sink_calls == 1U && strcmp(captured, "has needle here\n") == 0 &&
        lock_calls == 4U && unlock_calls == 4U;
}

unsigned open_cfw_test_easylogger_output_truncation(void)
{
    char message[1101];
    unsigned index;
    reset_state();
    enable_logger(0U);
    for (index = 0U; index < 1100U; ++index) {
        message[index] = 'A';
    }
    message[1100] = '\0';
    open_cfw_bootloader_easylogger_output_4176ce(
        4U, "boot", NULL, NULL, 0L, "%s", message);
    if (sink_calls != 1U || captured_length != 1020U ||
            captured[1019] != '\n' || captured[1020] != '\0') {
        return 0U;
    }
    for (index = 0U; index < 1019U; ++index) {
        if (captured[index] != 'A') {
            return 0U;
        }
    }
    return 1U;
}
