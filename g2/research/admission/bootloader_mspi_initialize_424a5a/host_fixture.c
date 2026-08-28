/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_initialize_candidate.h"

static uint8_t states[OPEN_CFW_MSPI_MODULE_COUNT][OPEN_CFW_MSPI_STATE_BYTES];
static void *last_handle;

static void put32(uint8_t *p, uint32_t v)
{
    p[0]=(uint8_t)v; p[1]=(uint8_t)(v>>8U); p[2]=(uint8_t)(v>>16U); p[3]=(uint8_t)(v>>24U);
}

void open_cfw_test_mspi_initialize_reset(uint8_t fill, uint32_t module, uint32_t prefix)
{
    uint32_t i, j;
    for (i=0U;i<OPEN_CFW_MSPI_MODULE_COUNT;i++)
        for (j=0U;j<OPEN_CFW_MSPI_STATE_BYTES;j++) states[i][j]=fill;
    if (module < OPEN_CFW_MSPI_MODULE_COUNT) put32(states[module], prefix);
    last_handle=0;
}

uint32_t open_cfw_test_mspi_initialize_run(uint32_t module, uint32_t provide_handle)
{
    return open_cfw_bootloader_mspi_initialize_424a5a(
        module, provide_handle ? &last_handle : (void **)0, states);
}

uint32_t open_cfw_test_mspi_initialize_read(uint32_t module, uint32_t offset, uint32_t width)
{
    uint8_t *p;
    if (module >= OPEN_CFW_MSPI_MODULE_COUNT || offset >= OPEN_CFW_MSPI_STATE_BYTES) return 0xFFFFFFFFU;
    p=&states[module][offset];
    if (width == 1U) return p[0];
    if (width == 4U && offset + 4U <= OPEN_CFW_MSPI_STATE_BYTES)
        return (uint32_t)p[0] | ((uint32_t)p[1]<<8U) | ((uint32_t)p[2]<<16U) | ((uint32_t)p[3]<<24U);
    return 0xFFFFFFFFU;
}

uint32_t open_cfw_test_mspi_initialize_handle_module(void)
{
    uint32_t i;
    for (i=0U;i<OPEN_CFW_MSPI_MODULE_COUNT;i++) if (last_handle == states[i]) return i;
    return 0xFFFFFFFFU;
}
