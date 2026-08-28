#include <stdint.h>

#define OPEN_CFW_MSPI_WRITE_LATCH_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_write_latch_420984.c"

static uint32_t transfer_status;
static uint32_t transfer_count;
static uint32_t command_value;
static uint32_t address_value;
static uint32_t length_value;
static uintptr_t data_value;
static uint32_t option_value;
static uint32_t log_count;
static uint32_t log_level;
static uint32_t log_line;
static uint32_t log_format;
static uint32_t log_function;

open_cfw_write_latch_u32 open_cfw_write_latch_host_transfer(
    open_cfw_write_latch_u32 command, open_cfw_write_latch_u32 address,
    open_cfw_write_latch_u32 length, const open_cfw_write_latch_u8 *data,
    open_cfw_write_latch_u32 option)
{
    ++transfer_count;
    command_value = command;
    address_value = address;
    length_value = length;
    data_value = (uintptr_t)data;
    option_value = option;
    return transfer_status;
}

void open_cfw_write_latch_host_log(
    open_cfw_write_latch_u32 level, open_cfw_write_latch_u32 line,
    open_cfw_write_latch_u32 format, open_cfw_write_latch_u32 function)
{
    ++log_count;
    log_level = level;
    log_line = line;
    log_format = format;
    log_function = function;
}

void open_cfw_write_latch_fixture_reset(void)
{
    transfer_status = 0U;
    transfer_count = 0U;
    command_value = 0U;
    address_value = 0U;
    length_value = 0U;
    data_value = 1U;
    option_value = 0U;
    log_count = 0U;
    log_level = 0U;
    log_line = 0U;
    log_format = 0U;
    log_function = 0U;
}

void open_cfw_write_latch_fixture_status(uint32_t value)
{
    transfer_status = value;
}

uint32_t open_cfw_write_latch_fixture_value(uint32_t field)
{
    switch (field) {
    case 0U: return transfer_count;
    case 1U: return command_value;
    case 2U: return address_value;
    case 3U: return length_value;
    case 4U: return (uint32_t)data_value;
    case 5U: return option_value;
    case 6U: return log_count;
    case 7U: return log_level;
    case 8U: return log_line;
    case 9U: return log_format;
    default: return log_function;
    }
}
