/* SPDX-License-Identifier: BSD-3-Clause */
#include "../../components/bootloader/core_overlay/runtime_mspi_configure_424af0.h"

static open_cfw_mspi_config_u8
    states[OPEN_CFW_MSPI_CONFIG_MODULES][OPEN_CFW_MSPI_CONFIG_STATE_BYTES];
static open_cfw_mspi_config_u8
    registers[OPEN_CFW_MSPI_CONFIG_MODULES][OPEN_CFW_MSPI_CONFIG_REGISTER_BYTES];
static open_cfw_mspi_configuration_424af0 configuration;
static open_cfw_mspi_config_u32 handle_module;

static void put32(open_cfw_mspi_config_u8 *pointer,
                  open_cfw_mspi_config_u32 value)
{
    pointer[0] = (open_cfw_mspi_config_u8)value;
    pointer[1] = (open_cfw_mspi_config_u8)(value >> 8U);
    pointer[2] = (open_cfw_mspi_config_u8)(value >> 16U);
    pointer[3] = (open_cfw_mspi_config_u8)(value >> 24U);
}

void open_cfw_test_mspi_configure_reset(
    open_cfw_mspi_config_u32 module, open_cfw_mspi_config_u32 prefix,
    open_cfw_mspi_config_u32 size, open_cfw_mspi_config_u32 tcb,
    open_cfw_mspi_config_u32 clock_on_d4, open_cfw_mspi_config_u32 xip,
    open_cfw_mspi_config_u32 scrambling, open_cfw_mspi_config_u32 axi)
{
    open_cfw_mspi_config_u32 row;
    open_cfw_mspi_config_u32 column;
    for (row = 0U; row < OPEN_CFW_MSPI_CONFIG_MODULES; row++) {
        for (column = 0U; column < OPEN_CFW_MSPI_CONFIG_STATE_BYTES; column++)
            states[row][column] = 0xA5U;
        for (column = 0U; column < OPEN_CFW_MSPI_CONFIG_REGISTER_BYTES; column++)
            registers[row][column] = 0xA5U;
        put32(registers[row] + 0x90U, xip);
        put32(registers[row] + 0x9CU, scrambling);
        put32(registers[row] + 0x80U, axi);
    }
    handle_module = module;
    if (module < OPEN_CFW_MSPI_CONFIG_MODULES) {
        put32(states[module], prefix);
        put32(states[module] + 4U, module);
    }
    configuration.tcb_size_words = size;
    configuration.tcb_address = tcb;
    configuration.clock_on_d4 = (open_cfw_mspi_config_u8)clock_on_d4;
}

open_cfw_mspi_config_u32 open_cfw_test_mspi_configure_run(
    open_cfw_mspi_config_u32 null_handle)
{
    open_cfw_mspi_config_u8 *handle =
        (null_handle != 0U || handle_module >= OPEN_CFW_MSPI_CONFIG_MODULES)
        ? (open_cfw_mspi_config_u8 *)0 : states[handle_module];
    return open_cfw_bootloader_mspi_configure_424af0(
        handle, &configuration, states, registers);
}

open_cfw_mspi_config_u32 open_cfw_test_mspi_configure_state(
    open_cfw_mspi_config_u32 module, open_cfw_mspi_config_u32 offset,
    open_cfw_mspi_config_u32 width)
{
    open_cfw_mspi_config_u8 *pointer;
    if (module >= OPEN_CFW_MSPI_CONFIG_MODULES ||
        offset >= OPEN_CFW_MSPI_CONFIG_STATE_BYTES) return 0xFFFFFFFFU;
    pointer = &states[module][offset];
    if (width == 1U) return pointer[0];
    if (width == 4U && offset + 4U <= OPEN_CFW_MSPI_CONFIG_STATE_BYTES)
        return (open_cfw_mspi_config_u32)pointer[0] |
               ((open_cfw_mspi_config_u32)pointer[1] << 8U) |
               ((open_cfw_mspi_config_u32)pointer[2] << 16U) |
               ((open_cfw_mspi_config_u32)pointer[3] << 24U);
    return 0xFFFFFFFFU;
}

open_cfw_mspi_config_u32 open_cfw_test_mspi_configure_register(
    open_cfw_mspi_config_u32 module, open_cfw_mspi_config_u32 selector)
{
    open_cfw_mspi_config_u32 offset;
    if (module >= OPEN_CFW_MSPI_CONFIG_MODULES) return 0xFFFFFFFFU;
    offset = selector == 0U ? 0x80U : selector == 1U ? 0x90U :
             selector == 2U ? 0x9CU : 0xFFFFFFFFU;
    if (offset == 0xFFFFFFFFU) return offset;
    return (open_cfw_mspi_config_u32)registers[module][offset] |
           ((open_cfw_mspi_config_u32)registers[module][offset + 1U] << 8U) |
           ((open_cfw_mspi_config_u32)registers[module][offset + 2U] << 16U) |
           ((open_cfw_mspi_config_u32)registers[module][offset + 3U] << 24U);
}

#include "../../components/bootloader/core_overlay/runtime_mspi_configure_424af0.c"
