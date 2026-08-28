#include <stdint.h>

#define OPEN_CFW_MSPI_SET_SERIAL_MODE_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_set_serial_mode_420f10.c"

static const open_cfw_serial_u8 serial_template[24] = {
    0x08, 0x03, 0x00, 0x00, 0x03, 0x00, 0x02, 0x00,
    0x00, 0x00, 0x00, 0x14, 0x00, 0x01, 0x01, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};
static open_cfw_serial_u32 values[16];
static open_cfw_serial_u32 events[8];
static open_cfw_serial_u32 event_count;

static void event(open_cfw_serial_u32 value)
{
    if (event_count < 8U) events[event_count] = value;
    ++event_count;
}

void open_cfw_serial_fixture_reset(void)
{
    open_cfw_serial_u32 i;
    for (i = 0U; i < 16U; ++i) values[i] = 0U;
    for (i = 0U; i < 8U; ++i) events[i] = 0U;
    values[0] = 0x12345678U;
    event_count = 0U;
}

void open_cfw_serial_fixture_config(open_cfw_serial_u32 field,
    open_cfw_serial_u32 value)
{
    if (field < 16U) values[field] = value;
}

open_cfw_serial_u32 open_cfw_serial_fixture_value(open_cfw_serial_u32 field)
{
    if (field == 32U) return event_count;
    if (field >= 64U && field < 72U) return events[field - 64U];
    return field < 16U ? values[field] : 0U;
}

const open_cfw_serial_u8 *open_cfw_serial_host_template(void)
{
    return serial_template;
}

open_cfw_serial_word open_cfw_serial_host_handle(void) { return values[0]; }

open_cfw_serial_u32 open_cfw_serial_host_reconfigure(
    const open_cfw_serial_u8 *config)
{
    event(1U);
    values[3] = config == serial_template ? 1U : 0U;
    values[4] = config[0];
    values[5] = config[8];
    return values[1];
}

void open_cfw_serial_host_xip(open_cfw_serial_u32 enabled)
{
    event(2U);
    values[6] = enabled;
}

open_cfw_serial_u32 open_cfw_serial_host_control(void *handle,
    open_cfw_serial_u32 request, void *argument)
{
    event(3U);
    values[7] = (open_cfw_serial_u32)(open_cfw_serial_word)handle;
    values[8] = request;
    values[9] = *(const open_cfw_serial_u8 *)argument;
    return values[2];
}

void open_cfw_serial_host_log(open_cfw_serial_u32 line,
    open_cfw_serial_u32 format)
{
    event(4U);
    values[10] = line;
    values[11] = format;
}
