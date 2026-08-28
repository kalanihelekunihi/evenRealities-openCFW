#include <stdint.h>
#include <stddef.h>

#define OPEN_CFW_MSPI_READ_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_read_420f70.c"

static uint32_t values[32];
static uint32_t events[16];
static uint32_t event_count;

void open_cfw_mspi_read_fixture_reset(void)
{
    uint32_t i;
    for (i = 0U; i < 32U; ++i) values[i] = 0U;
    for (i = 0U; i < 16U; ++i) events[i] = 0U;
    values[0] = 0x12345678U;
    event_count = 0U;
}

void open_cfw_mspi_read_fixture_config(uint32_t field, uint32_t value)
{
    if (field < 32U) values[field] = value;
}

uint32_t open_cfw_mspi_read_fixture_value(uint32_t field)
{
    if (field == 32U) return event_count;
    if (field >= 64U && field < 80U) return events[field - 64U];
    return field < 32U ? values[field] : 0U;
}

open_cfw_mspi_read_word open_cfw_mspi_read_host_handle(void)
{
    return (open_cfw_mspi_read_word)values[0];
}

void open_cfw_mspi_read_host_event(open_cfw_mspi_read_u32 event)
{
    if (event_count < 16U) events[event_count++] = event;
}

open_cfw_mspi_read_u32 open_cfw_mspi_read_host_wait(void)
{
    values[3] += 1U;
    return values[1];
}

open_cfw_mspi_read_u32 open_cfw_mspi_read_host_hal(void *handle,
    const open_cfw_mspi_read_descriptor *descriptor,
    open_cfw_mspi_read_u32 timeout)
{
    const uint8_t *raw = (const uint8_t *)descriptor;
    uint32_t i;
    values[4] += 1U;
    values[5] = (uint32_t)(uintptr_t)handle;
    values[6] = timeout;
    values[7] = descriptor->length;
    values[8] = descriptor->address_present;
    values[9] = descriptor->address;
    values[10] = descriptor->instruction_present;
    values[11] = descriptor->instruction;
    values[12] = descriptor->direction;
    values[13] = descriptor->buffer;
    values[14] = 0U;
    for (i = 0U; i < 24U; ++i) {
        if ((i >= 4U && i <= 6U) || i == 13U ||
            (i >= 17U && i <= 19U)) {
            values[14] |= (uint32_t)raw[i] << i;
        }
    }
    return values[2];
}
