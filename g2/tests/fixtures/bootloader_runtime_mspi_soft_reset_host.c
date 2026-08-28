#define OPEN_CFW_MSPI_SOFT_RESET_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_soft_reset_42052a.c"

static open_cfw_soft_reset_u32 statuses[2];
static open_cfw_soft_reset_u32 events[8][2];
static open_cfw_soft_reset_u32 event_count;

void open_cfw_soft_reset_fixture_reset(void)
{
    statuses[0] = 0U;
    statuses[1] = 0U;
    event_count = 0U;
}

void open_cfw_soft_reset_fixture_status(
    open_cfw_soft_reset_u32 index, open_cfw_soft_reset_u32 status)
{
    statuses[index] = status;
}

open_cfw_soft_reset_u32 open_cfw_soft_reset_host_command(
    open_cfw_soft_reset_u32 command)
{
    events[event_count][0] = 0U;
    events[event_count++][1] = command;
    return statuses[command == 0x99U ? 1U : 0U];
}

void open_cfw_soft_reset_host_delay(open_cfw_soft_reset_u32 duration)
{
    events[event_count][0] = 1U;
    events[event_count++][1] = duration;
}

void open_cfw_soft_reset_host_log(
    open_cfw_soft_reset_u32 line, open_cfw_soft_reset_u32 format)
{
    events[event_count][0] = line;
    events[event_count++][1] = format;
}

open_cfw_soft_reset_u32 open_cfw_soft_reset_fixture_count(void)
{
    return event_count;
}

open_cfw_soft_reset_u32 open_cfw_soft_reset_fixture_event(
    open_cfw_soft_reset_u32 index, open_cfw_soft_reset_u32 field)
{
    return events[index][field];
}
