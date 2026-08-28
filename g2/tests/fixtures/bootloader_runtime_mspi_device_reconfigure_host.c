#include <stdint.h>

#define OPEN_CFW_MSPI_DEVICE_RECONFIGURE_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_device_reconfigure_420e08.c"

enum { OPEN_CFW_RECONFIGURE_MAX_EVENTS = 16 };

static open_cfw_reconfigure_u32 values[32];
static open_cfw_reconfigure_u32 events[OPEN_CFW_RECONFIGURE_MAX_EVENTS];
static open_cfw_reconfigure_u32 event_count;
static open_cfw_reconfigure_u32 state_instance;

void open_cfw_reconfigure_fixture_reset(void)
{
    open_cfw_reconfigure_u32 index;
    for (index = 0U; index < 32U; ++index) values[index] = 0U;
    for (index = 0U; index < OPEN_CFW_RECONFIGURE_MAX_EVENTS; ++index)
        events[index] = 0U;
    values[0] = 0x12345678U;
    state_instance = 1U;
    event_count = 0U;
}

void open_cfw_reconfigure_fixture_config(open_cfw_reconfigure_u32 field,
    open_cfw_reconfigure_u32 value)
{
    if (field < 32U) values[field] = value;
    if (field == 31U) state_instance = value;
}

open_cfw_reconfigure_u32 open_cfw_reconfigure_fixture_value(
    open_cfw_reconfigure_u32 field)
{
    if (field == 32U) return event_count;
    if (field >= 64U && field < 64U + OPEN_CFW_RECONFIGURE_MAX_EVENTS)
        return events[field - 64U];
    return field < 32U ? values[field] : 0U;
}

static void open_cfw_reconfigure_event(open_cfw_reconfigure_u32 event)
{
    if (event_count < OPEN_CFW_RECONFIGURE_MAX_EVENTS)
        events[event_count] = event;
    ++event_count;
}

open_cfw_reconfigure_word open_cfw_reconfigure_host_handle(void)
{
    return values[0];
}

open_cfw_reconfigure_word open_cfw_reconfigure_host_state(void)
{
    return (open_cfw_reconfigure_word)&state_instance;
}

open_cfw_reconfigure_u32 open_cfw_reconfigure_host_call(
    open_cfw_reconfigure_u32 operation, open_cfw_reconfigure_word handle,
    open_cfw_reconfigure_word config)
{
    open_cfw_reconfigure_event(operation + 1U);
    values[8U + operation] = (open_cfw_reconfigure_u32)handle;
    if (operation == 1U) values[11] = config != 0U ? 1U : 0U;
    ++values[16U + operation];
    return values[1U + operation];
}

void open_cfw_reconfigure_host_pin_groups(open_cfw_reconfigure_u32 instance,
    open_cfw_reconfigure_u32 device)
{
    open_cfw_reconfigure_event(4U);
    values[12] = instance;
    values[13] = device;
    ++values[19];
}

void open_cfw_reconfigure_host_log(open_cfw_reconfigure_u32 line,
    open_cfw_reconfigure_u32 format)
{
    open_cfw_reconfigure_event(5U);
    values[14] = line;
    values[15] = format;
    ++values[20];
}
