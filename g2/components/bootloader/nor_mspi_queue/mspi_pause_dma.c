/* SPDX-License-Identifier: MIT
 * Combined source reconstruction of stock 0x4240aa, 0x423fb8, and 0x42403e.
 * Peripherals are memory-mapped state. Delay and clock APIs are explicit
 * providers; the delay fixture may model status evolution but no real elapsed
 * time or physical progress is assumed.
 */
#include "mspi_pause_dma.h"
#include <stdint.h>

#define MSPI_BASE UINT32_C(0x40060000)
#define PAUSE_TIMEOUT UINT32_C(0x186a0)

extern uint32_t opencfw_bl_critical_save(void);
extern void opencfw_hal_delay_us(uint32_t raw_count);
extern uint32_t opencfw_hal_status_poll(uint32_t count, uintptr_t address,
                                       uint32_t mask, uint32_t expected,
                                       uint32_t equal);
extern uint32_t opencfw_bl_clock_request(uint32_t clock, uint32_t user);

static volatile uint32_t *mspi_reg(uint32_t module, uint32_t offset)
{
    const uint32_t address = MSPI_BASE + (module << 12) + offset;
    return (volatile uint32_t *)(uintptr_t)address;
}

static uint32_t mspi_cq_pause(uint32_t *state)
{
    const uint32_t module = state[1];
    uint32_t remaining = PAUSE_TIMEOUT;

    *mspi_reg(module, 0x2b4u) = UINT32_C(0x00800000);
    for (;;) {
        const uint32_t control = *mspi_reg(module, 0x2a0u);
        if ((control & 1u) == 0u)
            break;

        if ((*mspi_reg(module, 0x2acu) & 8u) != 0u &&
            ((*mspi_reg(module, 0x2b8u) >> 7) & 1u) != 0u)
            break;

        if (remaining == 0u)
            return 4u;
        opencfw_hal_delay_us(1u);
        --remaining;
    }

    return opencfw_hal_status_poll(PAUSE_TIMEOUT,
        (uintptr_t)mspi_reg(module, 0x104u), 1u, 0u, 1u);
}

static uint32_t program_dma(uint32_t *state)
{
    const uint32_t module = state[1];
    const uint32_t next_index = state[0x850u / 4u] + 1u;
    const uint32_t ring_size = state[0x848u / 4u];
    const uint32_t quotient = ring_size != 0u ? next_index / ring_size : 0u;
    const uint32_t slot = next_index - ring_size * quotient;
    const uintptr_t descriptor_base = state[0x854u / 4u];
    const volatile uint32_t *const descriptor =
        (const volatile uint32_t *)(descriptor_base + slot * 0x18u);
    const uint32_t status = opencfw_bl_clock_request(
        4u, (module + 0x10u) & 0xffu);

    if (status != 0u)
        return status;

    *mspi_reg(module, 0x100u) = 0u;
    *mspi_reg(module, 0x108u) = descriptor[0];
    *mspi_reg(module, 0x10cu) = descriptor[1];
    *mspi_reg(module, 0x110u) = descriptor[2];
    *mspi_reg(module, 0x100u) = descriptor[3];
    return 0u;
}

uint32_t opencfw_provider_4240aa(uint32_t *state_address,
                                uint32_t timeout_increment)
{
    volatile uint32_t *const state = (volatile uint32_t *)state_address;
    const uint32_t previous_mask = opencfw_bl_critical_save();
    const uint32_t previous_timeout = state[0x840u / 4u];

    state[0x840u / 4u] = previous_timeout + timeout_increment;
    __asm__ volatile("msr primask, %0" :: "r"(previous_mask) : "memory");
    if (previous_timeout != 0u)
        return 0u;

    const uint32_t pause_status = mspi_cq_pause((uint32_t *)state_address);
    if (pause_status != 0u)
        return pause_status;

    state[0x24u / 4u] = 0u;
    *mspi_reg(state[1], 0x208u) = 0x40u;
    *mspi_reg(state[1], 0x200u) |= 0x40u;
    *(volatile uint8_t *)((uintptr_t)state_address + 0x83cu) = 1u;
    return program_dma((uint32_t *)state_address);
}
