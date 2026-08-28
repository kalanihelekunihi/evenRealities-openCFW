/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_device_configure_candidate.h"

enum { OPEN_CFW_DEVICE_MAX_WRITES = 3 };

typedef struct open_cfw_device_fixture {
    uint32_t devcfg;
    uint32_t devxip;
    uint32_t read_count;
    uint32_t write_count;
    uint32_t addresses[OPEN_CFW_DEVICE_MAX_WRITES];
    uint32_t values[OPEN_CFW_DEVICE_MAX_WRITES];
} open_cfw_device_fixture;

static open_cfw_device_fixture fixture;

static uint32_t read_reg(void *context, uint32_t address)
{
    open_cfw_device_fixture *state = context;
    state->read_count++;
    if ((address & 0xFFFU) == 0x84U) return state->devcfg;
    if ((address & 0xFFFU) == 0x90U) return state->devxip;
    return 0U;
}

static void write_reg(void *context, uint32_t address, uint32_t value)
{
    open_cfw_device_fixture *state = context;
    if (state->write_count < OPEN_CFW_DEVICE_MAX_WRITES) {
        state->addresses[state->write_count] = address;
        state->values[state->write_count] = value;
    }
    if ((address & 0xFFFU) == 0x84U) state->devcfg = value;
    if ((address & 0xFFFU) == 0x90U) state->devxip = value;
    state->write_count++;
}

void open_cfw_test_mspi_device_reset(uint32_t devcfg, uint32_t devxip)
{
    uint32_t index;
    fixture.devcfg = devcfg;
    fixture.devxip = devxip;
    fixture.read_count = 0U;
    fixture.write_count = 0U;
    for (index = 0U; index < OPEN_CFW_DEVICE_MAX_WRITES; index++) {
        fixture.addresses[index] = 0U;
        fixture.values[index] = 0U;
    }
}

uint32_t open_cfw_test_mspi_device_run(uint32_t module, uint32_t clock_on_d4,
                                       uint32_t device_configuration)
{
    const open_cfw_mspi_device_configure_context instance = {
        module, (uint8_t)clock_on_d4, (uint8_t)device_configuration
    };
    const open_cfw_mspi_device_configure_ports ports = {
        &fixture, read_reg, write_reg
    };
    return open_cfw_bootloader_mspi_device_configure_424120(&instance, &ports);
}

uint32_t open_cfw_test_mspi_device_value(uint32_t selector, uint32_t index)
{
    if (selector == 0U) return fixture.read_count;
    if (selector == 1U) return fixture.write_count;
    if (selector == 2U) return fixture.devcfg;
    if (selector == 3U) return fixture.devxip;
    if (selector == 4U && index < OPEN_CFW_DEVICE_MAX_WRITES)
        return fixture.addresses[index];
    if (selector == 5U && index < OPEN_CFW_DEVICE_MAX_WRITES)
        return fixture.values[index];
    return 0U;
}
