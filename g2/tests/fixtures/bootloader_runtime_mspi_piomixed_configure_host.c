/* SPDX-License-Identifier: BSD-3-Clause */
#include "../../components/bootloader/core_overlay/runtime_mspi_piomixed_configure_42488e.h"

typedef struct open_cfw_piomixed_fixture {
    open_cfw_mspi_pio_u32 register_value;
    open_cfw_mspi_pio_u32 read_count;
    open_cfw_mspi_pio_u32 write_count;
    open_cfw_mspi_pio_u32 address;
    open_cfw_mspi_pio_u32 written_value;
} open_cfw_piomixed_fixture;

static open_cfw_piomixed_fixture fixture;

static open_cfw_mspi_pio_u32 read_reg(void *context,
                                       open_cfw_mspi_pio_u32 address)
{
    open_cfw_piomixed_fixture *state = context;
    state->read_count++;
    state->address = address;
    return state->register_value;
}

static void write_reg(void *context, open_cfw_mspi_pio_u32 address,
                      open_cfw_mspi_pio_u32 value)
{
    open_cfw_piomixed_fixture *state = context;
    state->write_count++;
    state->address = address;
    state->written_value = value;
    state->register_value = value;
}

void open_cfw_test_mspi_piomixed_reset(open_cfw_mspi_pio_u32 value)
{
    fixture.register_value = value;
    fixture.read_count = 0U;
    fixture.write_count = 0U;
    fixture.address = 0U;
    fixture.written_value = 0U;
}

open_cfw_mspi_pio_u32 open_cfw_test_mspi_piomixed_run(
    open_cfw_mspi_pio_u32 module, open_cfw_mspi_pio_u32 configuration)
{
    const open_cfw_mspi_piomixed_state instance = {
        0U, module, 0U, 0U, 0U, (open_cfw_mspi_pio_u8)configuration
    };
    const open_cfw_mspi_piomixed_ports ports = {
        &fixture, read_reg, write_reg
    };
    return open_cfw_bootloader_mspi_piomixed_configure_42488e(&instance,
                                                               &ports);
}

open_cfw_mspi_pio_u32 open_cfw_test_mspi_piomixed_value(
    open_cfw_mspi_pio_u32 selector)
{
    if (selector == 0U) return fixture.read_count;
    if (selector == 1U) return fixture.write_count;
    if (selector == 2U) return fixture.address;
    if (selector == 3U) return fixture.written_value;
    return fixture.register_value;
}

#include "../../components/bootloader/core_overlay/runtime_mspi_piomixed_configure_42488e.c"
