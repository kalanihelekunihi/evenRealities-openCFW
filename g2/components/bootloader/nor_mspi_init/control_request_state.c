/* SPDX-License-Identifier: MIT
 * Exact bounded MSPI control requests 27 and 29.
 * CMDQ reset and pause/status are source providers; peripheral progress is
 * represented only by the synthetic fixture's MMIO and delay callbacks.
 */
#include "control_request_state.h"
#include "control_request_clock.h"
#include <stddef.h>
#include <stdint.h>

#define MSPI_BASE UINT32_C(0x40060000)
#define PAUSE_TIMEOUT UINT32_C(0x186a0)

extern uint32_t opencfw_provider_427baa(uint32_t *queue);
extern uint32_t opencfw_hal_status_poll(uint32_t count, uintptr_t address,
                                        uint32_t mask, uint32_t expected,
                                        uint32_t equal);
extern void opencfw_hal_delay_us(uint32_t raw_count);

static volatile uint32_t *mspi_reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (MSPI_BASE + (module << 12) + offset);
}

static uint32_t pause_cq(uint32_t *state)
{
    const uint32_t module = state[1];
    uint32_t count = PAUSE_TIMEOUT;

    *mspi_reg(module, 0x2b4u) = 0x00800000u;
    for (;;) {
        if ((*mspi_reg(module, 0x2a0u) & 1u) == 0u)
            break;
        if ((*mspi_reg(module, 0x2acu) & 8u) != 0u &&
            (*mspi_reg(module, 0x2b8u) & 0x80u) != 0u)
            break;
        if (count == 0u)
            return 4u;
        opencfw_hal_delay_us(1u);
        --count;
    }
    return opencfw_hal_status_poll(PAUSE_TIMEOUT,
        (uintptr_t)mspi_reg(module, 0x104u), 1u, 0u, 1u);
}

static uint32_t request29(uint32_t *handle, const uint8_t *config)
{
    uint32_t requested;
    uint32_t old_mode;
    uint32_t status = 0u;

    if (config == NULL)
        return 6u;
    if (handle[6] == 0u)
        return 7u;

    requested = config[0] != 0u;
    old_mode = *(volatile uint8_t *)((uintptr_t)handle + 0x82cu);
    /* Stock compares the requested Boolean byte directly with the mode byte;
     * mode 2 therefore transitions through the pause path rather than being
     * treated as the same Boolean state as mode 1. */
    if (requested == old_mode)
        return 0u;
    if (old_mode == 0u) {
        if (handle[8] != 0u)
            return 7u;
    } else if (old_mode == 2u) {
        status = pause_cq(handle);
    }

    if (status != 0u)
        return status;
    /* The stock caller ignores the reset helper's return value. */
    (void)opencfw_provider_427baa((uint32_t *)(uintptr_t)handle[0x20a]);

    handle[7] = 0u;
    handle[0x20c] = 0u;
    handle[8] = 0u;
    *(volatile uint8_t *)((uintptr_t)handle + 0x82cu) = (uint8_t)requested;
    *(volatile uint8_t *)((uintptr_t)handle + 0x82du) = 1u;
    handle[0x217] = 0u;
    return 0u;
}

uint32_t opencfw_hal_mspi_control_state_request(uint32_t handle_address,
                                               uint32_t request,
                                               void *config)
{
    uint32_t *const handle = (uint32_t *)(uintptr_t)handle_address;
    switch ((uint8_t)request) {
    case 26u:
        return opencfw_hal_mspi_control_clock_request(handle_address,config);
    case 27u:
        return pause_cq(handle);
    case 29u:
        return request29(handle, (const uint8_t *)config);
    default:
        return 0xeeee0002u;
    }
}
