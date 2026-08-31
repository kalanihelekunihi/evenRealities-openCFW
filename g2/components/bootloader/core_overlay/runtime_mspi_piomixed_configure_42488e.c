/* SPDX-License-Identifier: BSD-3-Clause */
/* Structured AmbiqSuite 5.1.0-equivalent G2 MSPI PIO-mixed configuration. */

#include "runtime_mspi_piomixed_configure_42488e.h"

static open_cfw_mspi_pio_u32 open_cfw_mspi_piomixed_value(
    open_cfw_mspi_pio_u32 configuration)
{
    switch (configuration >> 1) {
    case 0U:
    case 1U:
    case 2U:
    case 3U:
    case 4U:
    case 5U:
    case 10U:
        return 0U;
    case 6U:
        return 1U;
    case 7U:
        return 3U;
    case 8U:
        return 5U;
    case 9U:
        return 7U;
    case 11U:
        return 9U;
    case 12U:
        return 11U;
    default:
        return 0U;
    }
}

#if defined(__arm__) || defined(__thumb__)
__attribute__((aligned(2)))
open_cfw_mspi_pio_u32 open_cfw_bootloader_mspi_piomixed_configure_42488e(
    const open_cfw_mspi_piomixed_state *instance)
{
    open_cfw_mspi_pio_u32 configuration = instance->pio_configuration;
    volatile open_cfw_mspi_pio_u32 *registers;
    open_cfw_mspi_pio_u32 value;

    if (configuration >= 26U) return 0U;
    registers = (volatile open_cfw_mspi_pio_u32 *)(__UINTPTR_TYPE__)(
        0x40060000U + instance->module * 0x1000U);
    value = registers[1];
    registers[1] = (value & ~0x0fU) |
                   open_cfw_mspi_piomixed_value(configuration);
    return 0U;
}
#else
open_cfw_mspi_pio_u32 open_cfw_bootloader_mspi_piomixed_configure_42488e(
    const open_cfw_mspi_piomixed_state *instance,
    const open_cfw_mspi_piomixed_ports *ports)
{
    open_cfw_mspi_pio_u32 configuration = instance->pio_configuration;
    open_cfw_mspi_pio_u32 address;
    open_cfw_mspi_pio_u32 value;

    if (configuration >= 26U) return 0U;
    address = 0x40060004U + instance->module * 0x1000U;
    value = ports->read_reg(ports->context, address);
    value = (value & ~0x0fU) | open_cfw_mspi_piomixed_value(configuration);
    ports->write_reg(ports->context, address, value);
    return 0U;
}
#endif
