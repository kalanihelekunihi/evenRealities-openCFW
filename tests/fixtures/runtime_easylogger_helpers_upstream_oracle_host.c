/*
 * MIT-licensed host oracle compiling the pristine authenticated EasyLogger
 * implementations selected for the shared G2 helper boundary.
 */

#include <setjmp.h>
#include <stdint.h>
#include <string.h>

#define LOG_TAG "elog"
#include <elog.h>

static jmp_buf open_cfw_oracle_easylogger_helpers_assert_jump;
static uint32_t open_cfw_oracle_easylogger_helpers_assert_trap_active;
static uint32_t open_cfw_oracle_easylogger_helpers_assert_count;
static uint32_t open_cfw_oracle_easylogger_helpers_assert_line;

ElogErrCode elog_port_init(void)
{
    return ELOG_NO_ERR;
}

ElogErrCode elog_port_deinit(void)
{
    return ELOG_NO_ERR;
}

ElogErrCode elog_async_init(void)
{
    return ELOG_NO_ERR;
}

ElogErrCode elog_async_deinit(void)
{
    return ELOG_NO_ERR;
}

void elog_async_enabled(bool enabled)
{
    (void)enabled;
}

void elog_async_output(uint8_t level, const char *log, size_t size)
{
    (void)level;
    (void)log;
    (void)size;
}

void elog_port_output(const char *log, size_t size)
{
    (void)log;
    (void)size;
}

void elog_port_output_lock(void)
{
}

void elog_port_output_unlock(void)
{
}

const char *elog_port_get_time(void)
{
    return "";
}

const char *elog_port_get_p_info(void)
{
    return "";
}

const char *elog_port_get_t_info(void)
{
    return "";
}

#include "../../third_party/easylogger/src/elog.c"
#include "../../third_party/easylogger/src/elog_utils.c"

static void open_cfw_oracle_easylogger_helpers_assert_hook(
    const char *expression,
    const char *function,
    size_t line
)
{
    (void)expression;
    (void)function;
    open_cfw_oracle_easylogger_helpers_assert_count++;
    open_cfw_oracle_easylogger_helpers_assert_line = (uint32_t)line;
    if (open_cfw_oracle_easylogger_helpers_assert_trap_active != 0U) {
        open_cfw_oracle_easylogger_helpers_assert_trap_active = 0U;
        longjmp(open_cfw_oracle_easylogger_helpers_assert_jump, 1);
    }
}

void open_cfw_oracle_easylogger_helpers_reset(void)
{
    memset(&elog, 0, sizeof(elog));
    memset(log_buf, 0, sizeof(log_buf));
    open_cfw_oracle_easylogger_helpers_assert_trap_active = 0U;
    open_cfw_oracle_easylogger_helpers_assert_count = 0U;
    open_cfw_oracle_easylogger_helpers_assert_line = 0U;
    elog_assert_hook = open_cfw_oracle_easylogger_helpers_assert_hook;
}

void open_cfw_oracle_easylogger_helpers_set_format(
    uint32_t level,
    uint32_t format_set
)
{
    elog.enabled_fmt_set[level] = (size_t)format_set;
}

uint32_t open_cfw_oracle_easylogger_helpers_get_assert_count(void)
{
    return open_cfw_oracle_easylogger_helpers_assert_count;
}

uint32_t open_cfw_oracle_easylogger_helpers_get_assert_line(void)
{
    return open_cfw_oracle_easylogger_helpers_assert_line;
}

uint32_t open_cfw_oracle_easylogger_helpers_strcpy(
    uint32_t current_length,
    char *destination,
    const char *source
)
{
    return (uint32_t)elog_strcpy(
        (size_t)current_length,
        destination,
        source
    );
}

uint32_t open_cfw_oracle_easylogger_helpers_get_fmt_enabled(
    uint32_t level,
    uint32_t format_set
)
{
    return get_fmt_enabled((uint8_t)level, (size_t)format_set);
}

uint32_t
open_cfw_oracle_easylogger_helpers_get_fmt_used_and_enabled_u32(
    uint32_t level,
    uint32_t format_set,
    uint32_t argument
)
{
    return get_fmt_used_and_enabled_u32(
        (uint8_t)level,
        (size_t)format_set,
        argument
    );
}

uint32_t
open_cfw_oracle_easylogger_helpers_get_fmt_used_and_enabled_ptr(
    uint32_t level,
    uint32_t format_set,
    const char *argument
)
{
    return get_fmt_used_and_enabled_ptr(
        (uint8_t)level,
        (size_t)format_set,
        argument
    );
}

uint32_t open_cfw_oracle_easylogger_helpers_call_strcpy_trapped(
    uint32_t current_length,
    char *destination,
    const char *source,
    uint32_t *copied
)
{
    open_cfw_oracle_easylogger_helpers_assert_trap_active = 1U;
    if (setjmp(open_cfw_oracle_easylogger_helpers_assert_jump) != 0) {
        return 1U;
    }
    *copied = (uint32_t)elog_strcpy(
        (size_t)current_length,
        destination,
        source
    );
    open_cfw_oracle_easylogger_helpers_assert_trap_active = 0U;
    return 0U;
}

uint32_t open_cfw_oracle_easylogger_helpers_call_get_fmt_trapped(
    uint32_t level,
    uint32_t format_set,
    uint32_t *enabled
)
{
    open_cfw_oracle_easylogger_helpers_assert_trap_active = 1U;
    if (setjmp(open_cfw_oracle_easylogger_helpers_assert_jump) != 0) {
        return 1U;
    }
    *enabled = get_fmt_enabled((uint8_t)level, (size_t)format_set);
    open_cfw_oracle_easylogger_helpers_assert_trap_active = 0U;
    return 0U;
}
