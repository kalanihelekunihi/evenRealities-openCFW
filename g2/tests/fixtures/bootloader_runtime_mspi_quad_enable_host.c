#include <stdint.h>

#define OPEN_CFW_MSPI_QUAD_ENABLE_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_quad_enable_420c5c.c"

enum { OPEN_CFW_QUAD_MAX_EVENTS = 32 };

static open_cfw_quad_u32 values[32];
static open_cfw_quad_u32 events[OPEN_CFW_QUAD_MAX_EVENTS];
static open_cfw_quad_u32 event_count;
static open_cfw_quad_u32 read_count;

void open_cfw_quad_fixture_reset(void)
{
    open_cfw_quad_u32 index;
    for (index = 0U; index < 32U; ++index) {
        values[index] = 0U;
        events[index] = 0U;
    }
    values[0] = 0x12345678U;
    event_count = 0U;
    read_count = 0U;
}

void open_cfw_quad_fixture_config(open_cfw_quad_u32 field,
    open_cfw_quad_u32 value)
{
    if (field < 32U) values[field] = value;
}

open_cfw_quad_u32 open_cfw_quad_fixture_value(open_cfw_quad_u32 field)
{
    if (field == 32U) return event_count;
    if (field >= 64U && field < 64U + OPEN_CFW_QUAD_MAX_EVENTS)
        return events[field - 64U];
    return field < 32U ? values[field] : 0U;
}

static void open_cfw_quad_event(open_cfw_quad_u32 event)
{
    if (event_count < OPEN_CFW_QUAD_MAX_EVENTS) events[event_count] = event;
    ++event_count;
}

open_cfw_quad_word open_cfw_quad_host_handle(void)
{
    return (open_cfw_quad_word)values[0];
}

open_cfw_quad_u32 open_cfw_quad_host_wait(void)
{
    open_cfw_quad_event(1U);
    ++values[16];
    return values[1];
}

open_cfw_quad_u32 open_cfw_quad_host_read(open_cfw_quad_u32 command,
    open_cfw_quad_u8 *value, open_cfw_quad_u32 length)
{
    open_cfw_quad_event(2U);
    values[8] = command;
    values[9] = length;
    *value = (open_cfw_quad_u8)(read_count == 0U ? values[2] : values[3]);
    ++read_count;
    ++values[17];
    if (read_count == 1U) return values[4];
    return values[7];
}

open_cfw_quad_u32 open_cfw_quad_host_enable(void)
{
    open_cfw_quad_event(3U);
    ++values[18];
    return values[5];
}

open_cfw_quad_u32 open_cfw_quad_host_write(open_cfw_quad_u32 command,
    const open_cfw_quad_u8 *value, open_cfw_quad_u32 length)
{
    open_cfw_quad_event(4U);
    values[10] = command;
    values[11] = length;
    values[12] = *value;
    ++values[19];
    return values[6];
}

void open_cfw_quad_host_log(open_cfw_quad_u32 line,
    open_cfw_quad_u32 format, open_cfw_quad_u32 operation)
{
    open_cfw_quad_event(5U);
    ++values[20];
    values[13] = line;
    values[14] = format;
    values[15] = operation;
}
