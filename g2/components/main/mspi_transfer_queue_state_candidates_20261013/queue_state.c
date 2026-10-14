/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 queue control selectors 28, 31, 32 and 33.
 * Other command-queue branches remain behind the full dispatcher gate.
 */
#include <stdint.h>

extern uint64_t g2_main_mspi_queue_activate_4bfe60(uint32_t, uint32_t);

static volatile uint32_t *word(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + module * 0x1000u + offset);
}

uint32_t g2_main_mspi_transfer_queue_state_candidate(
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
    if (operation != 28u && operation != 31u &&
        operation != 32u && operation != 33u)
        return 6u;

    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)controller;
    if (operation == 28u) {
        *word(module, 0x2b4u) = 0x80u;
        return 0u;
    }
    if (operation == 31u) {
        if (configuration == 0) return 6u;
        if (state[0x215] != 0u) return 7u;
        const uint32_t *const cfg = (const uint32_t *)configuration;
        state[0x214] = 0u;
        state[0x210] = state[0x214];
        state[0x213] = state[0x214] + 1u;
        state[0x215] = cfg[0];
        state[0x212] = cfg[1] / 24u;
        return 0u;
    }
    if (operation == 33u) {
        if (*(const volatile uint8_t *)(uintptr_t)(controller + 0x8c8u) == 0u)
            __asm__ volatile("dmb sy" ::: "memory");
        *word(module, 0x2b4u) = 0x20u;
        state[0x20e] = 0u;
        if (state[0x211] == 0u) {
            const uint32_t result =
                (uint32_t)g2_main_mspi_queue_activate_4bfe60(
                    controller, state[0x211]);
            if (result == 0u) state[0x211] = 0u;
            return result;
        }
        return 0u;
    }
    *word(module, 0x2b4u) = UINT32_C(0x200000);
    state[0x20e] = 1u;
    state[0x211] = 0u;
    return 0u;
}
