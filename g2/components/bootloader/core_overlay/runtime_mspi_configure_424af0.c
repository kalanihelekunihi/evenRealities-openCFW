/* SPDX-License-Identifier: BSD-3-Clause */
/* Structured AmbiqSuite 5.1.0-equivalent G2 MSPI controller configuration. */

#include "runtime_mspi_configure_424af0.h"

static __attribute__((always_inline)) inline open_cfw_mspi_config_u32
open_cfw_mspi_config_load32(const volatile open_cfw_mspi_config_u8 *pointer)
{
    return *(const volatile open_cfw_mspi_config_u32 *)(const volatile void *)pointer;
}

static __attribute__((always_inline)) inline void open_cfw_mspi_config_store32(
    volatile open_cfw_mspi_config_u8 *pointer, open_cfw_mspi_config_u32 value)
{
    *(volatile open_cfw_mspi_config_u32 *)(volatile void *)pointer = value;
}

static __attribute__((always_inline)) inline open_cfw_mspi_config_u32
open_cfw_mspi_configure_state(
    volatile open_cfw_mspi_config_u8 *state,
    const open_cfw_mspi_configuration_424af0 *configuration,
    volatile open_cfw_mspi_config_u8 *registers)
{
    open_cfw_mspi_config_u32 maximum;
    open_cfw_mspi_config_u32 end;

    open_cfw_mspi_config_store32(registers + 0x90U,
        open_cfw_mspi_config_load32(registers + 0x90U) & ~1U);
    open_cfw_mspi_config_store32(registers + 0x9CU, 0U);
    open_cfw_mspi_config_store32(registers + 0x80U, 0U);
    open_cfw_mspi_config_store32(state + 0x18U, configuration->tcb_address);
    open_cfw_mspi_config_store32(state + 0x14U, configuration->tcb_size_words);
    if (configuration->tcb_address != 0U) {
        end = configuration->tcb_address + configuration->tcb_size_words * 4U;
        state[0x8C8U] = end < 0x20080000U ? 1U : 0U;
        maximum = ((configuration->tcb_size_words - 8U) * 4U) / 72U;
        if (maximum > 256U) maximum = 256U;
        open_cfw_mspi_config_store32(state + 0x858U, maximum);
    }
    state[9U] = configuration->clock_on_d4;
    state[8U] = 1U;
    state[10U] = 26U;
    return OPEN_CFW_MSPI_CONFIG_SUCCESS;
}

#if defined(__arm__) || defined(__thumb__)
__attribute__((aligned(2)))
open_cfw_mspi_config_u32 open_cfw_bootloader_mspi_configure_424af0(
    void *handle, const open_cfw_mspi_configuration_424af0 *configuration)
{
    volatile open_cfw_mspi_config_u8 *state;
    volatile open_cfw_mspi_config_u8 *registers;
    open_cfw_mspi_config_u32 prefix;
    open_cfw_mspi_config_u32 module;

    if (handle == (void *)0) return OPEN_CFW_MSPI_CONFIG_INVALID_HANDLE;
    state = (volatile open_cfw_mspi_config_u8 *)handle;
    prefix = open_cfw_mspi_config_load32(state);
    if ((prefix & 0x01FFFFFFU) != 0x01BEBEBEU)
        return OPEN_CFW_MSPI_CONFIG_INVALID_HANDLE;
    if ((prefix & 0x02000000U) != 0U)
        return OPEN_CFW_MSPI_CONFIG_INVALID_OPERATION;
    module = open_cfw_mspi_config_load32(state + 4U);
    registers = (volatile open_cfw_mspi_config_u8 *)(__UINTPTR_TYPE__)(
        0x40060000U + module * 0x1000U);
    return open_cfw_mspi_configure_state(state, configuration, registers);
}
#else
open_cfw_mspi_config_u32 open_cfw_bootloader_mspi_configure_424af0(
    open_cfw_mspi_config_u8 *handle,
    const open_cfw_mspi_configuration_424af0 *configuration,
    open_cfw_mspi_config_u8
        states[OPEN_CFW_MSPI_CONFIG_MODULES][OPEN_CFW_MSPI_CONFIG_STATE_BYTES],
    open_cfw_mspi_config_u8
        registers[OPEN_CFW_MSPI_CONFIG_MODULES][OPEN_CFW_MSPI_CONFIG_REGISTER_BYTES])
{
    open_cfw_mspi_config_u32 prefix;
    open_cfw_mspi_config_u32 module;
    if (handle == (open_cfw_mspi_config_u8 *)0)
        return OPEN_CFW_MSPI_CONFIG_INVALID_HANDLE;
    prefix = open_cfw_mspi_config_load32(handle);
    if ((prefix & 0x01FFFFFFU) != 0x01BEBEBEU)
        return OPEN_CFW_MSPI_CONFIG_INVALID_HANDLE;
    if ((prefix & 0x02000000U) != 0U)
        return OPEN_CFW_MSPI_CONFIG_INVALID_OPERATION;
    module = open_cfw_mspi_config_load32(handle + 4U);
    if (module >= OPEN_CFW_MSPI_CONFIG_MODULES || handle != states[module])
        return OPEN_CFW_MSPI_CONFIG_INVALID_HANDLE;
    return open_cfw_mspi_configure_state(handle, configuration,
                                         registers[module]);
}
#endif
