/* SPDX-License-Identifier: MIT
 * Requests 31 and 33 from stock HAL control dispatcher 0x4251c0.
 * This file intentionally does not cover the separate request-34 descriptor
 * transaction, whose mode-flag, block-release, and CQ-enable callees remain
 * outside this provider.
 */
#include "control_request_extension.h"
#include "../nor_mspi_queue/mspi_pause_dma.h"
#include <stddef.h>
#include <stdint.h>

static volatile uint32_t *mspi_reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + (module << 12) + offset);
}

static uint32_t request31(uint32_t *handle, const uint32_t *config)
{
    if (config == NULL)
        return 6u;
    if (handle[0x215] != 0u)
        return 7u;

    handle[0x214] = 0u;
    handle[0x210] = handle[0x214];
    handle[0x213] = handle[0x214] + 1u;
    handle[0x215] = config[0];
    handle[0x212] = config[1] / 0x18u;
    return 0u;
}

static uint32_t request33(uint32_t *handle, uint32_t module)
{
    if (*(volatile uint8_t *)((uintptr_t)handle + 0x8c8u) == 0u)
        __asm__ volatile("dmb sy" ::: "memory");
    *mspi_reg(module, 0x2b4u) = 0x20u;
    handle[0x20e] = 0u;

    if (handle[0x211] == 0u) {
        const uint32_t status = opencfw_provider_4240aa(handle, 0u);
        if (status != 0u)
            return status;
        handle[0x211] = 0u;
    }
    return 0u;
}

uint32_t opencfw_hal_mspi_control_queue_request(uint32_t handle_address,
                                                uint32_t request,
                                                void *config)
{
    uint32_t *const handle = (uint32_t *)(uintptr_t)handle_address;
    const uint32_t module = handle[1];

    switch ((uint8_t)request) {
    case 31u:
        return request31(handle, (const uint32_t *)config);
    case 33u:
        return request33(handle, module);
    default:
        /* Requests outside this bounded extension must remain visible to the
         * integrator; returning success would conceal an unrecovered path. */
        return 0xeeee0001u;
    }
}
