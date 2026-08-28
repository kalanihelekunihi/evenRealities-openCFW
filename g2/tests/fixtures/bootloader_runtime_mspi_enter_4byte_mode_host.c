#define OPEN_CFW_MSPI_ENTER_4BYTE_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_enter_4byte_mode_420890.c"

enum { EVENT_WAIT = 1U, EVENT_ENABLE = 2U, EVENT_WRITE = 3U,
       EVENT_MODE = 4U, EVENT_DISABLE = 5U, EVENT_LOG = 6U };
static open_cfw_enter_4byte_u32 config[7], events[16], event_count;
static open_cfw_enter_4byte_u32 wait_count, captured[8];

void open_cfw_enter_4byte_fixture_reset(void)
{
    open_cfw_enter_4byte_u32 i;
    for (i = 0U; i < 7U; ++i) config[i] = 0U;
    for (i = 0U; i < 16U; ++i) events[i] = 0U;
    for (i = 0U; i < 8U; ++i) captured[i] = 0U;
    config[0] = 1U;
    config[5] = 1U;
    event_count = wait_count = 0U;
}

void open_cfw_enter_4byte_fixture_config(
    open_cfw_enter_4byte_u32 field, open_cfw_enter_4byte_u32 value)
{
    config[field] = value;
}

static void event(open_cfw_enter_4byte_u32 value)
{
    if (event_count < 16U) events[event_count] = value;
    ++event_count;
}

open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_available(void)
{ return config[0]; }

open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_wait_ready(void)
{
    event(EVENT_WAIT);
    return config[(wait_count++ == 0U) ? 1U : 4U];
}

open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_write_enable(void)
{ event(EVENT_ENABLE); return config[2]; }

open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_write(
    open_cfw_enter_4byte_u32 command, open_cfw_enter_4byte_u32 address,
    open_cfw_enter_4byte_u32 unit, const open_cfw_enter_4byte_u8 *data,
    open_cfw_enter_4byte_u32 length)
{
    event(EVENT_WRITE);
    captured[0] = command; captured[1] = address; captured[2] = unit;
    captured[3] = (data == (const open_cfw_enter_4byte_u8 *)0);
    captured[4] = length;
    return config[3];
}

open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_is_4byte(void)
{ event(EVENT_MODE); return config[5]; }

open_cfw_enter_4byte_u32 open_cfw_enter_4byte_host_write_disable(void)
{ event(EVENT_DISABLE); return config[6]; }

void open_cfw_enter_4byte_host_log(
    open_cfw_enter_4byte_u32 line, open_cfw_enter_4byte_u32 format,
    open_cfw_enter_4byte_u32 function)
{
    event(EVENT_LOG);
    captured[5] = line; captured[6] = format; captured[7] = function;
}

open_cfw_enter_4byte_u32 open_cfw_enter_4byte_fixture_value(
    open_cfw_enter_4byte_u32 field)
{
    if (field < 8U) return captured[field];
    if (field == 8U) return event_count;
    return events[field - 9U];
}
