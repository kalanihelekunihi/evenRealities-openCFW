#include <stdint.h>
#include <string.h>

#define LOG_TAG "elog"
#include <elog.h>

static uint32_t open_cfw_oracle_easylogger_filter_assert_count;
static uint32_t open_cfw_oracle_easylogger_filter_lock_count;
static uint32_t open_cfw_oracle_easylogger_filter_unlock_count;

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
    open_cfw_oracle_easylogger_filter_lock_count++;
}

void elog_port_output_unlock(void)
{
    open_cfw_oracle_easylogger_filter_unlock_count++;
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

static void open_cfw_oracle_easylogger_filter_assert_hook(
    const char *expression,
    const char *function,
    size_t line
)
{
    (void)expression;
    (void)function;
    (void)line;
    open_cfw_oracle_easylogger_filter_assert_count++;
}

void open_cfw_oracle_easylogger_filter_reset(void)
{
    memset(&elog, 0, sizeof(elog));
    memset(log_buf, 0, sizeof(log_buf));
    open_cfw_oracle_easylogger_filter_assert_count = 0U;
    open_cfw_oracle_easylogger_filter_lock_count = 0U;
    open_cfw_oracle_easylogger_filter_unlock_count = 0U;
    elog_assert_hook = open_cfw_oracle_easylogger_filter_assert_hook;
}

void open_cfw_oracle_easylogger_filter_defaults(void)
{
    elog_set_filter_tag_lvl_default();
}

void open_cfw_oracle_easylogger_filter_write_u8(
    uint32_t offset,
    uint32_t value
)
{
    ((uint8_t *)&elog)[offset] = (uint8_t)value;
}

void open_cfw_oracle_easylogger_filter_set_init(uint32_t value)
{
    elog.init_ok = value != 0U;
}

uint32_t open_cfw_oracle_easylogger_filter_read_u8(uint32_t offset)
{
    return ((const uint8_t *)&elog)[offset];
}

uint32_t open_cfw_oracle_easylogger_filter_get_assert_count(void)
{
    return open_cfw_oracle_easylogger_filter_assert_count;
}

uint32_t open_cfw_oracle_easylogger_filter_get_lock_count(void)
{
    return open_cfw_oracle_easylogger_filter_lock_count;
}

uint32_t open_cfw_oracle_easylogger_filter_get_unlock_count(void)
{
    return open_cfw_oracle_easylogger_filter_unlock_count;
}
