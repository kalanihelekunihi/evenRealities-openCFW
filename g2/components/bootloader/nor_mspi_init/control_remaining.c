/* SPDX-License-Identifier: MIT
 * Recovered bounded request handlers from stock 0x4251c0.
 */
#include "control_remaining.h"
#include "control_request_extension.h"
#include "control_request34.h"
#include "control_request_state.h"
#include "control_request_transactions.h"
#include <stddef.h>
#include <stdint.h>

extern void opencfw_bl_mspi_device_configure_private(uint32_t *handle);

static volatile uint32_t *mspi_reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + (module << 12) + offset);
}

static void field(uint32_t module, uint32_t offset, uint32_t lsb,
                  uint32_t width, uint32_t value)
{
    volatile uint32_t *const reg = mspi_reg(module, offset);
    const uint32_t mask = ((UINT32_C(1) << width) - 1u) << lsb;
    *reg = (*reg & ~mask) | ((value << lsb) & mask);
}

static uint32_t request25(uint32_t handle, uint32_t module, void *config)
{
    volatile uint8_t *const state = (volatile uint8_t *)(uintptr_t)handle;
    const uint8_t *const p = (const uint8_t *)config;
    uint8_t mode;

    if (config == NULL)
        return 6u;
    mode = p[0];
    if ((module == 1u || module == 2u) &&
        (mode == 10u || mode == 11u))
        return 5u;

    state[10] = mode;
    opencfw_bl_mspi_device_configure_private((uint32_t *)(uintptr_t)handle);
    return 0u;
}

static uint32_t request35(uint32_t module, const uint8_t *p)
{
    uint32_t value;

    if (p == NULL)
        return 6u;
    if (p[0] >= 4u || p[1] >= 2u)
        return 6u;

    value = p[1] & 1u;
    field(module, 0x84u, 7u, 1u, value);
    field(module, 0x84u, 5u, 2u, p[0] & 3u);
    return 0u;
}

static uint32_t request36(uint32_t module, const uint8_t *p)
{
    if (p == NULL)
        return 6u;
    field(module, 0x84u, 26u, 6u, p[9] & 0x3fu);
    field(module, 0x90u, 8u, 4u, 5u);
    field(module, 0x90u, 13u, 1u, p[12]);
    return 0u;
}

static uint32_t request39(uint32_t module, const uint8_t *p)
{
    if (p == NULL)
        return 6u;
    if (p[4] == 0u) {
        field(module, 0xa4u, 0u, 1u, 0u);
        return 0u;
    }

    field(module, 0xa4u, 0u, 1u, 1u);
    field(module, 0xa4u, 9u, 2u, p[0] & 3u);
    field(module, 0xa4u, 1u, 1u, 0u);
    field(module, 0xa4u, 2u, 1u, 0u);
    field(module, 0xa4u, 3u, 1u, p[1]);
    field(module, 0xa4u, 4u, 1u, p[2]);
    field(module, 0xa4u, 5u, 1u, p[3]);
    field(module, 0xa4u, 6u, 1u, 0u);
    field(module, 0xa4u, 7u, 1u, 0u);
    field(module, 0xa4u, 8u, 1u, 0u);
    return 0u;
}

uint32_t opencfw_hal_mspi_control_remaining(uint32_t handle,
                                            uint32_t request,
                                            void *config)
{
    const uint32_t module = *(const volatile uint32_t *)(uintptr_t)
        (handle + 4u);
    const uint8_t *const p = (const uint8_t *)config;
    switch ((uint8_t)request) {
    case 25u:
        return request25(handle, module, config);
    case 26u:
    case 27u:
    case 29u:
        return opencfw_hal_mspi_control_state_request(handle, request, config);
    case 30u:
        return opencfw_hal_mspi_control_transaction_request(handle, request,
                                                             config);
    case 28u:
        if (*(const volatile uint8_t *)(uintptr_t)(handle + 0x8c8u) == 0u)
            __asm__ volatile("dmb sy" ::: "memory");
        *mspi_reg(module, 0x2b4u) = 0x80u;
        return 0u;
    case 31u:
    case 33u:
        return opencfw_hal_mspi_control_queue_request(handle, request, config);
    case 34u:
        return opencfw_hal_mspi_control_request34(handle, config);
    case 32u:
        *(volatile uint32_t *)(uintptr_t)(handle + 0x838u) = 1u;
        *(volatile uint32_t *)(uintptr_t)(handle + 0x844u) = 0u;
        *mspi_reg(module, 0x2b4u) = 0x00200000u;
        return 0u;
    case 35u:
        return request35(module, p);
    case 36u:
        return request36(module, p);
    case 37u:
        field(module, 0x90u, 6u, 1u, 0u);
        return 0u;
    case 38u:
        field(module, 0x90u, 6u, 1u, 1u);
        return 0u;
    case 39u:
        return request39(module, p);
    case 40u:
        return 6u;
    default:
        return 6u;
    }
}
