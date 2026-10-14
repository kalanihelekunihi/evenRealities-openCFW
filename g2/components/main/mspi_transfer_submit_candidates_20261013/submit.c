/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 selector 30: submit MSPI command-queue descriptors.
 * The complete transfer dispatcher remains a separate source gate.
 */
#include <stdint.h>

extern uint64_t g2_main_cq_reserve_538ece(uint32_t, uint32_t,
                                            uint32_t, uint32_t);
extern uint32_t g2_main_cq_commit_538fb4(uint32_t, uint32_t);
extern uint32_t g2_main_cq_commit_marker_5391d6(uint32_t, uint32_t);
extern uint32_t g2_main_cq_rollback_538f82(uint32_t);
extern uint32_t g2_main_mspi_queue_flags_4bfa10(uint32_t, uint32_t);
extern uint32_t g2_main_mspi_queue_start_4bfd44(uint32_t);
extern uint32_t g2_main_critical_save_473940(void);

static void restore(uint32_t previous)
{
    __asm__ volatile("msr primask, %0" :: "r"(previous) : "memory");
}

uint32_t g2_main_mspi_transfer_submit_candidate(uint32_t controller,
                                                  uint32_t selector,
                                                  const void *configuration)
{
    if (controller == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)controller &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;
    const uint32_t operation = selector & 0xffu;
    if (operation > 40u) return 6u;
    if (*(const volatile uint8_t *)(uintptr_t)(controller + 8u) == 0u)
        return 7u;
    if (operation != 30u) return 6u;
    if (configuration == 0) return 6u;

    const uint32_t *const cfg = (const uint32_t *)configuration;
    if ((cfg[1] & 0xe0u) != 0u ||
        (cfg[2] & UINT32_C(0x00e0e0e0)) != 0u)
        return 6u;
    volatile uint8_t *const handle =
        (volatile uint8_t *)(uintptr_t)controller;
    if (handle[0x82cu] != 1u) return 7u;
    const uint32_t module =
        *(volatile uint32_t *)(void *)(handle + 4u);
    const uint32_t base = UINT32_C(0x40060000) + module * 0x1000u;
    volatile uint32_t *const mode =
        (volatile uint32_t *)(void *)(handle + 0x838u);
    if (*mode != 0u) {
        *mode = 0u;
        if (handle[0x8c8u] == 0u)
            __asm__ volatile("dmb sy" ::: "memory");
        *(volatile uint32_t *)(uintptr_t)(base + 0x2b4u) = 0x20u;
    }

    const uint32_t queue =
        *(volatile uint32_t *)(void *)(handle + 0x828u);
    uint32_t prefix = 0u;
    uint32_t payload = 0u;
    if (((uint8_t)cfg[0] != 0u) && handle[0x82du] == 0u) {
        uint32_t slot_address = 0u;
        uint32_t index = 0u;
        uint32_t result = (uint32_t)g2_main_cq_reserve_538ece(
            queue, 1u, (uint32_t)(uintptr_t)&slot_address,
            (uint32_t)(uintptr_t)&index);
        if (result != 0u) return result;
        volatile uint32_t *const slot =
            (volatile uint32_t *)(uintptr_t)slot_address;
        volatile uint32_t *const state =
            (volatile uint32_t *)(void *)handle;
        state[(index & 0xffu) + 10u] = UINT32_C(0x004c072f);
        state[(index & 0xffu) + 0x10au] = controller;
        slot[0] = base + 0x2b4u;
        slot[1] = 0u;
        const uint32_t saved = g2_main_critical_save_473940();
        result = g2_main_cq_commit_538fb4(queue, 1u);
        if (result != 0u) {
            restore(saved);
            (void)g2_main_cq_rollback_538f82(queue);
            return result;
        }
        const uint32_t old_count = state[8];
        state[8] = old_count + 1u;
        restore(saved);
        if (old_count == 0u) {
            result = g2_main_mspi_queue_start_4bfd44(controller);
            if (result != 0u) return result;
        }
        prefix = 0x40u;
        payload = 0x400000u;
    }

    uint32_t slot_address = 0u;
    uint32_t index = 0u;
    uint32_t result = (uint32_t)g2_main_cq_reserve_538ece(
        queue, 3u, (uint32_t)(uintptr_t)&slot_address,
        (uint32_t)(uintptr_t)&index);
    if (result != 0u) return result;
    volatile uint32_t *const slot =
        (volatile uint32_t *)(uintptr_t)slot_address;
    slot[2] = base + 0x2b8u;
    slot[0] = slot[2];
    slot[4] = base + 0x2b4u;
    slot[1] = g2_main_mspi_queue_flags_4bfa10(
        controller, prefix | cfg[1]);
    slot[3] = 0x4000u;
    slot[5] = payload | cfg[2];

    const uint32_t saved = g2_main_critical_save_473940();
    if ((uint8_t)cfg[0] == 0u)
        result = g2_main_cq_commit_538fb4(queue, 0u);
    else
        result = g2_main_cq_commit_marker_5391d6(queue, 0u);
    if (result == 0u) {
        volatile uint32_t *const state =
            (volatile uint32_t *)(void *)handle;
        const uint32_t old_count = state[8];
        state[8] = old_count + 1u;
        handle[0x82cu] = (uint8_t)cfg[0] == 0u ? 0u : 2u;
        restore(saved);
        if (old_count == 0u)
            return g2_main_mspi_queue_start_4bfd44(controller);
        return 0u;
    }
    restore(saved);
    (void)g2_main_cq_rollback_538f82(queue);
    return result;
}
