/* SPDX-License-Identifier: BSD-3-Clause */
#include "../../components/bootloader/core_overlay/runtime_mspi_device_configure_public_424be4.h"

static open_cfw_mspi_public_u8 state[0x8D0U];
static open_cfw_mspi_public_config configuration;
static open_cfw_mspi_public_trace trace;

static void put32(open_cfw_mspi_public_u8 *pointer,
                  open_cfw_mspi_public_u32 value)
{
    pointer[0] = (open_cfw_mspi_public_u8)value;
    pointer[1] = (open_cfw_mspi_public_u8)(value >> 8U);
    pointer[2] = (open_cfw_mspi_public_u8)(value >> 16U);
    pointer[3] = (open_cfw_mspi_public_u8)(value >> 24U);
}

static open_cfw_mspi_public_u32 get32(const open_cfw_mspi_public_u8 *pointer)
{
    return (open_cfw_mspi_public_u32)pointer[0] |
           ((open_cfw_mspi_public_u32)pointer[1] << 8U) |
           ((open_cfw_mspi_public_u32)pointer[2] << 16U) |
           ((open_cfw_mspi_public_u32)pointer[3] << 24U);
}

void open_cfw_test_public_device_reset(
    open_cfw_mspi_public_u32 module, open_cfw_mspi_public_u32 prefix,
    open_cfw_mspi_public_u32 configured, open_cfw_mspi_public_u32 clock_source,
    open_cfw_mspi_public_u32 tcb, open_cfw_mspi_public_u32 frequency,
    open_cfw_mspi_public_u32 device, open_cfw_mspi_public_u32 release_status,
    open_cfw_mspi_public_u32 request_status)
{
    open_cfw_mspi_public_u32 index;
    for (index = 0U; index < sizeof(state); index++) state[index] = 0U;
    for (index = 0U; index < sizeof(configuration); index++)
        ((open_cfw_mspi_public_u8 *)&configuration)[index] = 0U;
    for (index = 0U; index < sizeof(trace); index++)
        ((open_cfw_mspi_public_u8 *)&trace)[index] = 0U;
    put32(state, prefix); put32(state + 4U, module);
    state[8U] = (open_cfw_mspi_public_u8)configured;
    state[0x8C9U] = (open_cfw_mspi_public_u8)clock_source;
    put32(state + 0x18U, tcb); put32(state + 0x8CCU, 99U);
    state[13U] = 1U;
    configuration.frequency = (open_cfw_mspi_public_u8)frequency;
    configuration.device = (open_cfw_mspi_public_u8)device;
    trace.release_status = release_status;
    trace.request_status = request_status;
}

open_cfw_mspi_public_u32 open_cfw_test_public_device_run(
    open_cfw_mspi_public_u32 null_state)
{
    return open_cfw_bootloader_mspi_device_configure_public_424be4(
        null_state != 0U ? (open_cfw_mspi_public_u8 *)0 : state,
        &configuration, &trace);
}

open_cfw_mspi_public_u32 open_cfw_test_public_device_state(
    open_cfw_mspi_public_u32 selector)
{
    if (selector == 0U) return state[0x8C9U];
    if (selector == 1U) return state[10U];
    if (selector == 2U) return state[13U];
    if (selector == 3U) return state[12U];
    if (selector == 4U) return get32(state + 0x10U);
    if (selector == 5U) return get32(state + 0x8CCU);
    return 0xFFFFFFFFU;
}

open_cfw_mspi_public_u32 open_cfw_test_public_device_trace(
    open_cfw_mspi_public_u32 selector)
{
    const open_cfw_mspi_public_u32 *words =
        (const open_cfw_mspi_public_u32 *)(const void *)&trace;
    return selector < sizeof(trace) / sizeof(words[0])
        ? words[selector] : 0xFFFFFFFFU;
}

#include "../../components/bootloader/core_overlay/runtime_mspi_device_configure_public_424be4.c"
