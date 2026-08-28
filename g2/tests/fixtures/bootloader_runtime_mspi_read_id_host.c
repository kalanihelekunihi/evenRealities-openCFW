#define OPEN_CFW_MSPI_READ_ID_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_read_id_42059e.c"

static open_cfw_read_id_u32 fixture_status;
static open_cfw_read_id_u8 fixture_bytes[3];
static open_cfw_read_id_u32 fixture_command;
static open_cfw_read_id_u32 fixture_length;
static open_cfw_read_id_u32 fixture_log_line;
static open_cfw_read_id_u32 fixture_log_format;

void open_cfw_read_id_fixture_reset(void)
{
    fixture_status = 0U;
    fixture_bytes[0] = 0U;
    fixture_bytes[1] = 0U;
    fixture_bytes[2] = 0U;
    fixture_command = 0U;
    fixture_length = 0U;
    fixture_log_line = 0U;
    fixture_log_format = 0U;
}

void open_cfw_read_id_fixture_response(
    open_cfw_read_id_u32 status, open_cfw_read_id_u32 bytes)
{
    fixture_status = status;
    fixture_bytes[0] = (open_cfw_read_id_u8)(bytes >> 16);
    fixture_bytes[1] = (open_cfw_read_id_u8)(bytes >> 8);
    fixture_bytes[2] = (open_cfw_read_id_u8)bytes;
}

open_cfw_read_id_u32 open_cfw_read_id_host_command(
    open_cfw_read_id_u32 command, open_cfw_read_id_u8 *bytes,
    open_cfw_read_id_u32 length)
{
    fixture_command = command;
    fixture_length = length;
    bytes[0] = fixture_bytes[0];
    bytes[1] = fixture_bytes[1];
    bytes[2] = fixture_bytes[2];
    return fixture_status;
}

void open_cfw_read_id_host_log(
    open_cfw_read_id_u32 line, open_cfw_read_id_u32 format)
{
    fixture_log_line = line;
    fixture_log_format = format;
}

open_cfw_read_id_u32 open_cfw_read_id_fixture_value(open_cfw_read_id_u32 field)
{
    const open_cfw_read_id_u32 values[] = {
        fixture_command, fixture_length, fixture_log_line, fixture_log_format
    };
    return values[field];
}
