/* SPDX-License-Identifier: BSD-3-Clause */
/* Structured AmbiqSuite 5.1.0-equivalent G2 MSPI state initializer. */

#include "runtime_mspi_initialize_424a5a.h"

static __attribute__((always_inline)) inline open_cfw_mspi_init_u32
open_cfw_mspi_init_load32(
    const open_cfw_mspi_init_u8 *pointer)
{
    return (open_cfw_mspi_init_u32)pointer[0] |
           ((open_cfw_mspi_init_u32)pointer[1] << 8U) |
           ((open_cfw_mspi_init_u32)pointer[2] << 16U) |
           ((open_cfw_mspi_init_u32)pointer[3] << 24U);
}

static __attribute__((always_inline)) inline void open_cfw_mspi_init_store32(
    open_cfw_mspi_init_u8 *pointer, open_cfw_mspi_init_u32 value)
{
    pointer[0] = (open_cfw_mspi_init_u8)value;
    pointer[1] = (open_cfw_mspi_init_u8)(value >> 8U);
    pointer[2] = (open_cfw_mspi_init_u8)(value >> 16U);
    pointer[3] = (open_cfw_mspi_init_u8)(value >> 24U);
}

static __attribute__((always_inline)) inline open_cfw_mspi_init_u32
open_cfw_mspi_initialize_state(
    open_cfw_mspi_init_u32 module, void **handle,
    open_cfw_mspi_init_u8 *state)
{
    open_cfw_mspi_init_u32 prefix = open_cfw_mspi_init_load32(state);

    if ((prefix & 0x01000000U) != 0U)
        return OPEN_CFW_MSPI_INIT_INVALID_OPERATION;
    open_cfw_mspi_init_store32(
        state, ((prefix | 0x01000000U) & 0xFF000000U) | 0x00BEBEBEU);
    open_cfw_mspi_init_store32(state + 4U, module);
    state[0x0CU] = 0U;
    open_cfw_mspi_init_store32(state + 0x18U, 0U);
    state[0x8C9U] = 7U;
    open_cfw_mspi_init_store32(state + 0x8CCU, 8U);
    *handle = state;
    return OPEN_CFW_MSPI_INIT_SUCCESS;
}

#if defined(__arm__) || defined(__thumb__)
__attribute__((aligned(2)))
open_cfw_mspi_init_u32 open_cfw_bootloader_mspi_initialize_424a5a(
    open_cfw_mspi_init_u32 module, void **handle)
{
    open_cfw_mspi_init_u8 *state;

    if (module >= OPEN_CFW_MSPI_INIT_MODULE_COUNT)
        return OPEN_CFW_MSPI_INIT_OUT_OF_RANGE;
    if (handle == (void **)0) return OPEN_CFW_MSPI_INIT_INVALID_ARG;
    state = (open_cfw_mspi_init_u8 *)(__UINTPTR_TYPE__)(
        0x2001CAA0U + module * OPEN_CFW_MSPI_INIT_STATE_BYTES);
    return open_cfw_mspi_initialize_state(module, handle, state);
}
#else
open_cfw_mspi_init_u32 open_cfw_bootloader_mspi_initialize_424a5a(
    open_cfw_mspi_init_u32 module, void **handle,
    open_cfw_mspi_init_u8
        states[OPEN_CFW_MSPI_INIT_MODULE_COUNT][OPEN_CFW_MSPI_INIT_STATE_BYTES])
{
    if (module >= OPEN_CFW_MSPI_INIT_MODULE_COUNT)
        return OPEN_CFW_MSPI_INIT_OUT_OF_RANGE;
    if (handle == (void **)0) return OPEN_CFW_MSPI_INIT_INVALID_ARG;
    return open_cfw_mspi_initialize_state(module, handle, states[module]);
}
#endif
