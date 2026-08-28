/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_piomixed_configure_candidate.h"

typedef struct open_cfw_piomixed_fixture {
    uint32_t register_value;
    uint32_t read_count;
    uint32_t write_count;
    uint32_t address;
    uint32_t written_value;
} open_cfw_piomixed_fixture;

static open_cfw_piomixed_fixture fixture;

static uint32_t read_reg(void *context, uint32_t address)
{
    open_cfw_piomixed_fixture *state = context;
    state->read_count++;
    state->address = address;
    return state->register_value;
}

static void write_reg(void *context, uint32_t address, uint32_t value)
{
    open_cfw_piomixed_fixture *state = context;
    state->write_count++;
    state->address = address;
    state->written_value = value;
    state->register_value = value;
}

void open_cfw_test_mspi_piomixed_reset(uint32_t value)
{
    fixture.register_value = value;
    fixture.read_count = 0U;
    fixture.write_count = 0U;
    fixture.address = 0U;
    fixture.written_value = 0U;
}

uint32_t open_cfw_test_mspi_piomixed_run(uint32_t module,
                                         uint32_t configuration)
{
    const open_cfw_mspi_piomixed_context instance = {
        module, (uint8_t)configuration
    };
    const open_cfw_mspi_piomixed_ports ports = {
        &fixture, read_reg, write_reg
    };
    return open_cfw_bootloader_mspi_piomixed_configure_42488e(&instance,
                                                               &ports);
}

uint32_t open_cfw_test_mspi_piomixed_value(uint32_t selector)
{
    if (selector == 0U) return fixture.read_count;
    if (selector == 1U) return fixture.write_count;
    if (selector == 2U) return fixture.address;
    if (selector == 3U) return fixture.written_value;
    return fixture.register_value;
}
