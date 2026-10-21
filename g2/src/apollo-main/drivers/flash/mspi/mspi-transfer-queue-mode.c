/* SPDX-License-Identifier: MIT
 * Main 0x4c0f78 selector 29. Full transfer dispatcher remains gated.
 */
#include <stdint.h>

extern uint64_t g2_main_mspi_queue_terminate_4bfd6e(uint32_t, uint32_t,
                                                      uint32_t, uint32_t);
extern uint32_t g2_main_queue_reset_53916e(uint32_t);

uint32_t g2_main_mspi_transfer_queue_mode_candidate(
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
    if (operation != 29u) return 6u;
    if (configuration == 0) return 6u;

    volatile uint8_t *const handle =
        (volatile uint8_t *)(uintptr_t)controller;
    if (*(volatile uint32_t *)(void *)(handle + 0x18u) == 0u)
        return 7u;
    const uint8_t enabled = *(const uint8_t *)configuration != 0u;
    const uint8_t current = handle[0x82cu];
    if (enabled == current) return 0u;
    if (current == 0u) {
        if (*(volatile uint32_t *)(void *)(handle + 0x20u) != 0u)
            return 7u;
    } else if (current == 2u) {
        const uint32_t result =
            (uint32_t)g2_main_mspi_queue_terminate_4bfd6e(
                controller, selector, (uint32_t)(uintptr_t)configuration, 0u);
        if (result != 0u) return result;
    }
    (void)g2_main_queue_reset_53916e(
        *(volatile uint32_t *)(void *)(handle + 0x828u));
    *(volatile uint32_t *)(void *)(handle + 0x1cu) = 0u;
    *(volatile uint32_t *)(void *)(handle + 0x830u) = 0u;
    *(volatile uint32_t *)(void *)(handle + 0x20u) = 0u;
    handle[0x82cu] = enabled;
    handle[0x82du] = 1u;
    *(volatile uint32_t *)(void *)(handle + 0x85cu) = 0u;
    return 0u;
}
