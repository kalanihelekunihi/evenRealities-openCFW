/* SPDX-License-Identifier: BSD-3-Clause */
#include "../../components/bootloader/core_overlay/runtime_mspi_initialize_424a5a.h"

static open_cfw_mspi_init_u8
    states[OPEN_CFW_MSPI_INIT_MODULE_COUNT][OPEN_CFW_MSPI_INIT_STATE_BYTES];
static void *last_handle;

static void put32(open_cfw_mspi_init_u8 *pointer,
                  open_cfw_mspi_init_u32 value)
{
    pointer[0] = (open_cfw_mspi_init_u8)value;
    pointer[1] = (open_cfw_mspi_init_u8)(value >> 8U);
    pointer[2] = (open_cfw_mspi_init_u8)(value >> 16U);
    pointer[3] = (open_cfw_mspi_init_u8)(value >> 24U);
}

void open_cfw_test_mspi_initialize_reset(open_cfw_mspi_init_u8 fill,
                                         open_cfw_mspi_init_u32 module,
                                         open_cfw_mspi_init_u32 prefix)
{
    open_cfw_mspi_init_u32 row;
    open_cfw_mspi_init_u32 column;
    for (row = 0U; row < OPEN_CFW_MSPI_INIT_MODULE_COUNT; row++)
        for (column = 0U; column < OPEN_CFW_MSPI_INIT_STATE_BYTES; column++)
            states[row][column] = fill;
    if (module < OPEN_CFW_MSPI_INIT_MODULE_COUNT)
        put32(states[module], prefix);
    last_handle = (void *)0;
}

open_cfw_mspi_init_u32 open_cfw_test_mspi_initialize_run(
    open_cfw_mspi_init_u32 module, open_cfw_mspi_init_u32 provide_handle)
{
    return open_cfw_bootloader_mspi_initialize_424a5a(
        module, provide_handle != 0U ? &last_handle : (void **)0, states);
}

open_cfw_mspi_init_u32 open_cfw_test_mspi_initialize_read(
    open_cfw_mspi_init_u32 module, open_cfw_mspi_init_u32 offset,
    open_cfw_mspi_init_u32 width)
{
    open_cfw_mspi_init_u8 *pointer;
    if (module >= OPEN_CFW_MSPI_INIT_MODULE_COUNT ||
        offset >= OPEN_CFW_MSPI_INIT_STATE_BYTES) return 0xFFFFFFFFU;
    pointer = &states[module][offset];
    if (width == 1U) return pointer[0];
    if (width == 4U && offset + 4U <= OPEN_CFW_MSPI_INIT_STATE_BYTES)
        return (open_cfw_mspi_init_u32)pointer[0] |
               ((open_cfw_mspi_init_u32)pointer[1] << 8U) |
               ((open_cfw_mspi_init_u32)pointer[2] << 16U) |
               ((open_cfw_mspi_init_u32)pointer[3] << 24U);
    return 0xFFFFFFFFU;
}

open_cfw_mspi_init_u32 open_cfw_test_mspi_initialize_handle_module(void)
{
    open_cfw_mspi_init_u32 module;
    for (module = 0U; module < OPEN_CFW_MSPI_INIT_MODULE_COUNT; module++)
        if (last_handle == states[module]) return module;
    return 0xFFFFFFFFU;
}

#include "../../components/bootloader/core_overlay/runtime_mspi_initialize_424a5a.c"
