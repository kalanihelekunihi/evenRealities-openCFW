#define OPEN_CFW_MSPI_4BYTE_MODE_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_4byte_mode_420800.c"

static open_cfw_4byte_mode_u32 read_status, register_byte, read_calls, log_calls;
static open_cfw_4byte_mode_u32 captured[8];

void open_cfw_4byte_mode_fixture_reset(void)
{
    open_cfw_4byte_mode_u32 i;
    read_status = register_byte = read_calls = log_calls = 0U;
    for (i = 0U; i < 8U; ++i) captured[i] = 0U;
}

void open_cfw_4byte_mode_fixture_config(
    open_cfw_4byte_mode_u32 status, open_cfw_4byte_mode_u32 value)
{
    read_status = status;
    register_byte = value;
}

open_cfw_4byte_mode_u32 open_cfw_4byte_mode_host_read(
    open_cfw_4byte_mode_u32 command, open_cfw_4byte_mode_u8 *bytes,
    open_cfw_4byte_mode_u32 length)
{
    ++read_calls;
    captured[0] = command;
    captured[1] = length;
    captured[2] = (open_cfw_4byte_mode_u32)bytes[0] |
        ((open_cfw_4byte_mode_u32)bytes[1] << 8) |
        ((open_cfw_4byte_mode_u32)bytes[2] << 16) |
        ((open_cfw_4byte_mode_u32)bytes[3] << 24);
    captured[3] = bytes[4];
    bytes[0] = (open_cfw_4byte_mode_u8)register_byte;
    return read_status;
}

void open_cfw_4byte_mode_host_log(
    open_cfw_4byte_mode_u32 line, open_cfw_4byte_mode_u32 format,
    open_cfw_4byte_mode_u32 function)
{
    ++log_calls;
    captured[4] = line;
    captured[5] = format;
    captured[6] = function;
}

open_cfw_4byte_mode_u32 open_cfw_4byte_mode_fixture_value(
    open_cfw_4byte_mode_u32 field)
{
    if (field == 7U) return read_calls;
    if (field == 8U) return log_calls;
    return captured[field];
}
