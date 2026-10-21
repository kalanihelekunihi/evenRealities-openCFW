/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 selector 34: submit a structured MSPI CQ descriptor.
 * Full transfer dispatcher remains a separate source gate.
 */
#include <stdint.h>

extern uint64_t g2_main_cq_reserve_538ece(uint32_t, uint32_t,
                                            uint32_t, uint32_t);
extern uint32_t g2_main_cq_commit_538fb4(uint32_t, uint32_t);
extern uint32_t g2_main_cq_rollback_538f82(uint32_t);
extern uint32_t g2_main_mspi_queue_flags_4bfa10(uint32_t, uint32_t);
extern uint32_t g2_main_mspi_queue_start_4bfd44(uint32_t);
extern uint32_t g2_main_critical_save_473940(void);

static void restore(uint32_t previous)
{
    __asm__ volatile("msr primask, %0" :: "r"(previous) : "memory");
}

uint32_t g2_main_mspi_transfer_descriptor_candidate(
    uint32_t controller, uint32_t selector, const void *configuration)
{
    if (controller == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)controller &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    const uint32_t operation = selector & 0xffu;
    if (operation > 40u) return 6u;
    if (*(const volatile uint8_t *)(uintptr_t)(controller + 8u) == 0u)
        return 7u;
    if (operation != 34u) return 6u;
    if (configuration == 0) return 6u;

    const uint32_t *const cfg = (const uint32_t *)configuration;
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)controller;
    const uint32_t queue = state[0x20au];
    if (queue == 0u) return 7u;
    if (state[8] == 0x100u) return 5u;
    uint32_t slot_address = 0u;
    uint32_t index = 0u;
    if ((uint32_t)g2_main_cq_reserve_538ece(
            queue, cfg[3] + 3u,
            (uint32_t)(uintptr_t)&slot_address,
            (uint32_t)(uintptr_t)&index) != 0u)
        return 5u;

    const uint32_t base = UINT32_C(0x40060000) +
                          state[1] * 0x1000u;
    volatile uint32_t *const slot =
        (volatile uint32_t *)(uintptr_t)slot_address;
    slot[0] = base + 0x2b8u;
    slot[1] = g2_main_mspi_queue_flags_4bfa10(controller, cfg[0]);
    const volatile uint32_t *const pairs =
        (const volatile uint32_t *)(uintptr_t)cfg[2];
    for (uint32_t i = 0u; i < cfg[3]; ++i) {
        slot[2u + i * 2u] = pairs[i * 2u];
        slot[3u + i * 2u] = pairs[i * 2u + 1u];
    }
    volatile uint32_t *const tail = slot + cfg[3] * 2u;
    if (cfg[6] != 0u)
        *(volatile uint32_t *)(uintptr_t)cfg[6] =
            (uint32_t)(uintptr_t)(tail + 2u);
    tail[2] = base + 0x2b8u;
    tail[3] = 0x4000u;
    tail[4] = base + 0x2b4u;
    tail[5] = cfg[1];

    uint32_t callback = cfg[4];
    if (callback == 0u && state[0x20eu] == 0u &&
        *(const volatile uint8_t *)(uintptr_t)(controller + 0x82cu) == 0u &&
        (state[0x216u] >> 1u) <= state[0x217u])
        callback = UINT32_C(0x004c072d);
    state[(index & 0xffu) + 10u] = callback;
    state[(index & 0xffu) + 0x10au] = cfg[5];

    const uint32_t saved = g2_main_critical_save_473940();
    const uint32_t result = g2_main_cq_commit_538fb4(
        queue, callback != 0u);
    if (result != 0u) {
        restore(saved);
        (void)g2_main_cq_rollback_538f82(queue);
        return result;
    }
    const uint32_t previous = state[8];
    state[8] = previous + 1u;
    state[0x20cu] += 1u;
    if (cfg[4] == 0u) {
        if (callback == 0u)
            state[0x217u] += 1u;
        else
            state[0x217u] = 0u;
    } else {
        *(volatile uint8_t *)(uintptr_t)(controller + 0x82du) = 0u;
        state[0x217u] = 0u;
    }
    restore(saved);
    if (previous == 0u)
        return g2_main_mspi_queue_start_4bfd44(controller);
    return 0u;
}
