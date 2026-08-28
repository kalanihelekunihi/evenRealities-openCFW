/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static uint8_t bypass_state;
static uint32_t calls[8];
static uint32_t call_count;

static void record(uint32_t operation)
{
    calls[call_count++] = operation;
}

uint8_t *open_cfw_mspi_guard_host_bypass(void)
{
    return &bypass_state;
}

void open_cfw_mspi_guard_host_acquire(void) { record(1U); }
void open_cfw_mspi_guard_host_disable(void) { record(2U); }
void open_cfw_mspi_guard_host_enable(void) { record(3U); }
void open_cfw_mspi_guard_host_release(void) { record(4U); }

#define OPEN_CFW_MSPI_GUARD_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_guard_41ff08.c"

void open_cfw_mspi_guard_fixture_reset(uint32_t bypass)
{
    uint32_t index;

    bypass_state = (uint8_t)bypass;
    call_count = 0U;
    for (index = 0U; index < 8U; ++index) {
        calls[index] = 0U;
    }
}

uint32_t open_cfw_mspi_guard_fixture_count(void) { return call_count; }

uint32_t open_cfw_mspi_guard_fixture_call(uint32_t index)
{
    return calls[index];
}
