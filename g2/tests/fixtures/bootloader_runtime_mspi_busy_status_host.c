#define OPEN_CFW_MSPI_BUSY_STATUS_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_busy_status_42074e.c"

static open_cfw_busy_status_u32 read_status;
static open_cfw_busy_status_u32 status_byte;
static open_cfw_busy_status_u32 read_calls;
static open_cfw_busy_status_u32 log_calls;
static open_cfw_busy_status_u32 captured[7];

void open_cfw_busy_status_fixture_reset(void)
{
    open_cfw_busy_status_u32 index;
    read_status = 0U;
    status_byte = 0U;
    read_calls = 0U;
    log_calls = 0U;
    for (index = 0U; index < 7U; ++index) {
        captured[index] = 0U;
    }
}

void open_cfw_busy_status_fixture_config(
    open_cfw_busy_status_u32 result,
    open_cfw_busy_status_u32 byte_value)
{
    read_status = result;
    status_byte = byte_value;
}

open_cfw_busy_status_u32 open_cfw_busy_status_host_read(
    open_cfw_busy_status_u32 command,
    open_cfw_busy_status_u8 *bytes,
    open_cfw_busy_status_u32 length)
{
    ++read_calls;
    captured[0] = command;
    captured[1] = length;
    captured[2] = (open_cfw_busy_status_u32)bytes[0] |
        ((open_cfw_busy_status_u32)bytes[1] << 8) |
        ((open_cfw_busy_status_u32)bytes[2] << 16) |
        ((open_cfw_busy_status_u32)bytes[3] << 24);
    captured[3] = bytes[4];
    bytes[0] = (open_cfw_busy_status_u8)status_byte;
    return read_status;
}

void open_cfw_busy_status_host_log(
    open_cfw_busy_status_u32 line,
    open_cfw_busy_status_u32 format,
    open_cfw_busy_status_u32 function)
{
    ++log_calls;
    captured[4] = line;
    captured[5] = format;
    captured[6] = function;
}

open_cfw_busy_status_u32 open_cfw_busy_status_fixture_value(
    open_cfw_busy_status_u32 field)
{
    if (field == 7U) return read_calls;
    if (field == 8U) return log_calls;
    return captured[field];
}
