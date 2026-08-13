/*
 * MIT-licensed host harness for the shared G2 EasyLogger helper adaptation.
 */

#include <setjmp.h>
#include <stdint.h>
#include <string.h>

#include "../../components/shared/easylogger/runtime_easylogger_helpers.h"

static struct open_cfw_easylogger_helpers_logger
    open_cfw_test_easylogger_helpers_logger;
static jmp_buf open_cfw_test_easylogger_helpers_assert_jump;
static uint32_t open_cfw_test_easylogger_helpers_assert_trap_active;
static uint32_t open_cfw_test_easylogger_helpers_assert_count;
static uint32_t open_cfw_test_easylogger_helpers_assert_line;

struct open_cfw_easylogger_helpers_logger *
open_cfw_easylogger_helpers_get_logger(void)
{
    return &open_cfw_test_easylogger_helpers_logger;
}

void open_cfw_easylogger_helpers_assert_failed(uint32_t recovered_line)
{
    open_cfw_test_easylogger_helpers_assert_count++;
    open_cfw_test_easylogger_helpers_assert_line = recovered_line;
    if (open_cfw_test_easylogger_helpers_assert_trap_active != 0U) {
        open_cfw_test_easylogger_helpers_assert_trap_active = 0U;
        longjmp(open_cfw_test_easylogger_helpers_assert_jump, 1);
    }
}

#include \
    "../../components/shared/easylogger/runtime_easylogger_helpers.c"

void open_cfw_test_easylogger_helpers_reset(void)
{
    memset(
        &open_cfw_test_easylogger_helpers_logger,
        0,
        sizeof(open_cfw_test_easylogger_helpers_logger)
    );
    open_cfw_test_easylogger_helpers_assert_trap_active = 0U;
    open_cfw_test_easylogger_helpers_assert_count = 0U;
    open_cfw_test_easylogger_helpers_assert_line = 0U;
}

void open_cfw_test_easylogger_helpers_set_format(
    uint32_t level,
    uint32_t format_set
)
{
    open_cfw_test_easylogger_helpers_logger.enabled_format_set[level] =
        format_set;
}

uint32_t open_cfw_test_easylogger_helpers_get_assert_count(void)
{
    return open_cfw_test_easylogger_helpers_assert_count;
}

uint32_t open_cfw_test_easylogger_helpers_get_assert_line(void)
{
    return open_cfw_test_easylogger_helpers_assert_line;
}

uint32_t open_cfw_test_easylogger_helpers_get_profile(void)
{
    return OPEN_CFW_EASYLOGGER_HELPERS_PROFILE;
}

uint32_t open_cfw_test_easylogger_helpers_get_state_address(void)
{
    return OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_STATE_ADDRESS;
}

uint32_t open_cfw_test_easylogger_helpers_get_assert_hook_address(void)
{
    return OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_HOOK_ADDRESS;
}

uint32_t open_cfw_test_easylogger_helpers_get_output_address(void)
{
    return OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_OUTPUT_ADDRESS;
}

uint32_t open_cfw_test_easylogger_helpers_get_assert_wait_address(void)
{
    return OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_WAIT_ADDRESS;
}

uint32_t open_cfw_test_easylogger_helpers_get_line_buffer_size(void)
{
    return OPEN_CFW_EASYLOGGER_HELPERS_LINE_BUFFER_SIZE;
}

uint32_t open_cfw_test_easylogger_helpers_get_level_count(void)
{
    return OPEN_CFW_EASYLOGGER_HELPERS_LEVEL_COUNT;
}

uint32_t open_cfw_test_easylogger_helpers_get_tag_level_size(void)
{
    return sizeof(struct open_cfw_easylogger_helpers_tag_level);
}

uint32_t open_cfw_test_easylogger_helpers_get_tag_offset(void)
{
    return __builtin_offsetof(
        struct open_cfw_easylogger_helpers_tag_level,
        tag
    );
}

uint32_t open_cfw_test_easylogger_helpers_get_tag_use_flag_offset(void)
{
    return __builtin_offsetof(
        struct open_cfw_easylogger_helpers_tag_level,
        tag_use_flag
    );
}

uint32_t open_cfw_test_easylogger_helpers_get_logger_size(void)
{
    return sizeof(struct open_cfw_easylogger_helpers_logger);
}

uint32_t open_cfw_test_easylogger_helpers_get_enabled_format_offset(void)
{
    return __builtin_offsetof(
        struct open_cfw_easylogger_helpers_logger,
        enabled_format_set
    );
}

uint32_t open_cfw_test_easylogger_helpers_call_strcpy_trapped(
    uint32_t current_length,
    char *destination,
    const char *source,
    uint32_t *copied
)
{
    open_cfw_test_easylogger_helpers_assert_trap_active = 1U;
    if (setjmp(open_cfw_test_easylogger_helpers_assert_jump) != 0) {
        return 1U;
    }
    *copied = open_cfw_easylogger_strcpy(
        current_length,
        destination,
        source
    );
    open_cfw_test_easylogger_helpers_assert_trap_active = 0U;
    return 0U;
}

uint32_t open_cfw_test_easylogger_helpers_call_get_fmt_trapped(
    uint32_t level,
    uint32_t format_set,
    uint32_t *enabled
)
{
    open_cfw_test_easylogger_helpers_assert_trap_active = 1U;
    if (setjmp(open_cfw_test_easylogger_helpers_assert_jump) != 0) {
        return 1U;
    }
    *enabled = open_cfw_easylogger_get_fmt_enabled(
        (open_cfw_easylogger_helpers_u8)level,
        format_set
    );
    open_cfw_test_easylogger_helpers_assert_trap_active = 0U;
    return 0U;
}
