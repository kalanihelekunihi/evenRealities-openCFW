/* SPDX-License-Identifier: BSD-3-Clause */
/* Structured AmbiqSuite 5.1.0-equivalent G2 MSPI device-mode configuration. */

#include "runtime_mspi_device_configure_424120.h"

typedef struct open_cfw_mspi_device_mode {
    open_cfw_mspi_dev_u32 device;
    open_cfw_mspi_dev_u32 separate_io;
    open_cfw_mspi_dev_u32 mixed;
    open_cfw_mspi_dev_u32 pad_output;
    open_cfw_mspi_dev_u32 d4_pad_output;
} open_cfw_mspi_device_mode;

static open_cfw_mspi_device_mode open_cfw_mspi_device_mode_for(
    open_cfw_mspi_dev_u32 configuration)
{
    open_cfw_mspi_device_mode mode = {
        (configuration & 1U) + 1U, 0U, 0U, 0x103U, 0x80000013U
    };
    switch (configuration >> 1) {
    case 0U:
        mode.separate_io = 1U;
        break;
    case 1U:
        mode.device += 4U;
        break;
    case 2U:
        mode.device += 8U;
        mode.pad_output = 0x10fU;
        mode.d4_pad_output = 0x8000001fU;
        break;
    case 3U:
    case 4U:
        mode.device += 12U;
        mode.pad_output = 0x3ffU;
        mode.d4_pad_output = 0U;
        break;
    case 5U:
        mode.device += 16U;
        mode.pad_output = 0x7ffffU;
        mode.d4_pad_output = 0U;
        break;
    case 6U:
        mode.mixed = 1U;
        break;
    case 7U:
        mode.mixed = 3U;
        break;
    case 8U:
        mode.mixed = 5U;
        mode.pad_output = 0x10fU;
        mode.d4_pad_output = 0x8000001fU;
        break;
    case 9U:
        mode.mixed = 7U;
        mode.pad_output = 0x10fU;
        mode.d4_pad_output = 0x8000001fU;
        break;
    case 10U:
        break;
    case 11U:
        mode.mixed = 9U;
        mode.pad_output = 0x3ffU;
        mode.d4_pad_output = 0U;
        break;
    case 12U:
        mode.mixed = 11U;
        mode.pad_output = 0x3ffU;
        mode.d4_pad_output = 0U;
        break;
    default:
        mode.device = 0U;
        break;
    }
    return mode;
}

#if defined(__arm__) || defined(__thumb__)
open_cfw_mspi_dev_u32 open_cfw_bootloader_mspi_device_configure_424120(
    const open_cfw_mspi_device_state *instance)
{
    open_cfw_mspi_dev_u32 configuration = instance->device_configuration;
    open_cfw_mspi_device_mode mode;
    volatile open_cfw_mspi_dev_u32 *registers;
    open_cfw_mspi_dev_u32 value;
    open_cfw_mspi_dev_u32 pad_output;

    if (configuration >= 26U) return 0U;
    mode = open_cfw_mspi_device_mode_for(configuration);
    registers = (volatile open_cfw_mspi_dev_u32 *)(__UINTPTR_TYPE__)(
        0x40060000U + instance->module * 0x1000U);
    value = registers[0x84U / 4U];
    value = (value & ~0x1fU) | mode.device;
    value = (value & ~(1UL << 25)) | (mode.separate_io << 25);
    registers[0x84U / 4U] = value;
    value = registers[0x90U / 4U];
    value = (value & ~(0x0fUL << 8)) | (mode.mixed << 8);
    registers[0x90U / 4U] = value;
    pad_output = mode.pad_output;
    if (instance->clock_on_d4 != 0U && mode.d4_pad_output != 0U)
        pad_output = mode.d4_pad_output;
    registers[0x44U / 4U] = pad_output;
    return 0U;
}
#else
open_cfw_mspi_dev_u32 open_cfw_bootloader_mspi_device_configure_424120(
    const open_cfw_mspi_device_state *instance,
    const open_cfw_mspi_device_ports *ports)
{
    open_cfw_mspi_dev_u32 configuration = instance->device_configuration;
    open_cfw_mspi_device_mode mode;
    open_cfw_mspi_dev_u32 base;
    open_cfw_mspi_dev_u32 value;
    open_cfw_mspi_dev_u32 pad_output;

    if (configuration >= 26U) return 0U;
    mode = open_cfw_mspi_device_mode_for(configuration);
    base = 0x40060000U + instance->module * 0x1000U;
    value = ports->read_reg(ports->context, base + 0x84U);
    value = (value & ~0x1fU) | mode.device;
    value = (value & ~(1UL << 25)) | (mode.separate_io << 25);
    ports->write_reg(ports->context, base + 0x84U, value);
    value = ports->read_reg(ports->context, base + 0x90U);
    value = (value & ~(0x0fUL << 8)) | (mode.mixed << 8);
    ports->write_reg(ports->context, base + 0x90U, value);
    pad_output = mode.pad_output;
    if (instance->clock_on_d4 != 0U && mode.d4_pad_output != 0U)
        pad_output = mode.d4_pad_output;
    ports->write_reg(ports->context, base + 0x44U, pad_output);
    return 0U;
}
#endif
