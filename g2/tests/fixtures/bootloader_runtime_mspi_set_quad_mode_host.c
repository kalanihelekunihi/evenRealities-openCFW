#include <stdint.h>

#define OPEN_CFW_MSPI_SET_QUAD_MODE_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_set_quad_mode_420e8c.c"

enum { OPEN_CFW_QUAD_MAX_EVENTS = 12 };

static const open_cfw_quad_u8 stock_template[OPEN_CFW_QUAD_CONFIG_SIZE] = {
    0x08, 0x03, 0x00, 0x00, 0x6B, 0x00, 0x02, 0x00,
    0x10, 0x00, 0x00, 0x14, 0x00, 0x01, 0x01, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};
static open_cfw_quad_u8 observed_config[OPEN_CFW_QUAD_CONFIG_SIZE];
static open_cfw_quad_u32 values[16];
static open_cfw_quad_u32 events[OPEN_CFW_QUAD_MAX_EVENTS];
static open_cfw_quad_u32 event_count;

static void open_cfw_quad_event(open_cfw_quad_u32 event)
{
    if (event_count < OPEN_CFW_QUAD_MAX_EVENTS) events[event_count] = event;
    ++event_count;
}

void open_cfw_quad_fixture_reset(void)
{
    open_cfw_quad_u32 index;
    for (index = 0U; index < 16U; ++index) values[index] = 0U;
    for (index = 0U; index < OPEN_CFW_QUAD_MAX_EVENTS; ++index)
        events[index] = 0U;
    for (index = 0U; index < OPEN_CFW_QUAD_CONFIG_SIZE; ++index)
        observed_config[index] = 0U;
    values[0] = 0x12345678U;
    event_count = 0U;
}

void open_cfw_quad_fixture_config(open_cfw_quad_u32 field,
    open_cfw_quad_u32 value)
{
    if (field < 16U) values[field] = value;
}

open_cfw_quad_u32 open_cfw_quad_fixture_value(open_cfw_quad_u32 field)
{
    if (field == 32U) return event_count;
    if (field >= 64U && field < 64U + OPEN_CFW_QUAD_MAX_EVENTS)
        return events[field - 64U];
    if (field >= 100U && field < 100U + OPEN_CFW_QUAD_CONFIG_SIZE)
        return observed_config[field - 100U];
    return field < 16U ? values[field] : 0U;
}

const open_cfw_quad_u8 *open_cfw_quad_host_template(void)
{
    return stock_template;
}

open_cfw_quad_word open_cfw_quad_host_handle(void)
{
    return values[0];
}

void open_cfw_quad_host_copy(void *destination, const void *source,
    open_cfw_quad_u32 count)
{
    open_cfw_quad_u32 index;
    open_cfw_quad_u8 *output = (open_cfw_quad_u8 *)destination;
    const open_cfw_quad_u8 *input = (const open_cfw_quad_u8 *)source;
    open_cfw_quad_event(1U);
    values[3] = count;
    for (index = 0U; index < count; ++index) output[index] = input[index];
}

open_cfw_quad_u32 open_cfw_quad_host_reconfigure(
    const open_cfw_quad_u8 *config)
{
    open_cfw_quad_u32 index;
    open_cfw_quad_event(2U);
    for (index = 0U; index < OPEN_CFW_QUAD_CONFIG_SIZE; ++index)
        observed_config[index] = config[index];
    return values[1];
}

void open_cfw_quad_host_xip(open_cfw_quad_u32 enabled)
{
    open_cfw_quad_event(3U);
    values[4] = enabled;
}

open_cfw_quad_u32 open_cfw_quad_host_control(void *handle,
    open_cfw_quad_u32 request, void *argument)
{
    open_cfw_quad_event(4U);
    values[5] = (open_cfw_quad_u32)(open_cfw_quad_word)handle;
    values[6] = request;
    values[7] = *(const open_cfw_quad_u8 *)argument;
    return values[2];
}

void open_cfw_quad_host_log(open_cfw_quad_u32 line,
    open_cfw_quad_u32 format)
{
    open_cfw_quad_event(5U);
    values[8] = line;
    values[9] = format;
    ++values[10];
}
