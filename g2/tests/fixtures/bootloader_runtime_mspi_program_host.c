#include <stdint.h>
#include <stddef.h>

#define OPEN_CFW_MSPI_PROGRAM_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_program_420b0c.c"

enum { MAX_EVENTS = 128, MAX_TRANSFERS = 32 };

static uint32_t values[64];
static uint32_t events[MAX_EVENTS];
static uint32_t event_count;
static uint32_t transfer_count;
static uint32_t transfer_address[MAX_TRANSFERS];
static uint32_t transfer_length[MAX_TRANSFERS];
static uintptr_t transfer_buffer[MAX_TRANSFERS];

void open_cfw_program_fixture_reset(void)
{
    uint32_t i;
    for (i = 0; i < 64U; ++i) values[i] = 0U;
    for (i = 0; i < MAX_EVENTS; ++i) events[i] = 0U;
    for (i = 0; i < MAX_TRANSFERS; ++i) {
        transfer_address[i] = 0U;
        transfer_length[i] = 0U;
        transfer_buffer[i] = 0U;
    }
    values[0] = 0x12345678U;
    event_count = 0U;
    transfer_count = 0U;
}

void open_cfw_program_fixture_config(uint32_t field, uint32_t value)
{
    if (field < 64U) values[field] = value;
}

uint32_t open_cfw_program_fixture_value(uint32_t field)
{
    if (field == 32U) return event_count;
    if (field == 33U) return transfer_count;
    if (field >= 128U && field < 128U + MAX_EVENTS)
        return events[field - 128U];
    if (field >= 256U && field < 256U + MAX_TRANSFERS)
        return transfer_address[field - 256U];
    if (field >= 320U && field < 320U + MAX_TRANSFERS)
        return transfer_length[field - 320U];
    if (field >= 384U && field < 384U + MAX_TRANSFERS)
        return (uint32_t)transfer_buffer[field - 384U];
    return field < 64U ? values[field] : 0U;
}

open_cfw_program_word open_cfw_program_host_handle(void)
{
    return (open_cfw_program_word)values[0];
}

void open_cfw_program_host_event(open_cfw_program_u32 event)
{
    if (event_count < MAX_EVENTS) events[event_count++] = event;
}

static uint32_t stage_result(uint32_t stage)
{
    values[stage + 16U] += 1U;
    if (values[1] == stage &&
        (values[2] == 0U || values[stage + 16U] == values[2]))
        return values[3];
    return 0U;
}

open_cfw_program_u32 open_cfw_program_host_wait_default(void)
{
    open_cfw_program_host_event(5U);
    return stage_result(1U);
}

open_cfw_program_u32 open_cfw_program_host_enable(void)
{
    open_cfw_program_host_event(6U);
    return stage_result(2U);
}

open_cfw_program_u32 open_cfw_program_host_transfer(open_cfw_program_u32 cmd,
    open_cfw_program_u32 address, open_cfw_program_u32 address_flag,
    const open_cfw_program_u8 *buffer, open_cfw_program_u32 length)
{
    open_cfw_program_host_event(7U);
    values[8] = cmd;
    values[9] = address_flag;
    if (transfer_count < MAX_TRANSFERS) {
        transfer_address[transfer_count] = address;
        transfer_length[transfer_count] = length;
        transfer_buffer[transfer_count] = (uintptr_t)buffer;
    }
    transfer_count += 1U;
    return stage_result(3U);
}

open_cfw_program_u32 open_cfw_program_host_wait(open_cfw_program_u32 limit)
{
    open_cfw_program_host_event(8U);
    values[10] = limit;
    return stage_result(4U);
}

open_cfw_program_u32 open_cfw_program_host_disable(void)
{
    open_cfw_program_host_event(9U);
    return stage_result(5U);
}

void open_cfw_program_host_diag(open_cfw_program_u32 format,
    open_cfw_program_u32 first, open_cfw_program_word second,
    open_cfw_program_u32 third)
{
    values[11] += 1U;
    values[12] = format;
    values[13] = first;
    values[14] = (uint32_t)second;
    values[15] = third;
}
