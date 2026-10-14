/* SPDX-License-Identifier: MIT
 * Main 0x4bfe60: update command queue count and launch its first descriptor.
 */
#include <stdint.h>

extern uint32_t g2_main_critical_save_473940(void);
extern uint64_t g2_main_mspi_queue_terminate_4bfd6e(uint32_t, uint32_t,
                                                      uint32_t, uint32_t);
extern uint64_t g2_main_mspi_queue_descriptor_4bfdf4(uint32_t, uint32_t,
                                                       uint32_t, uint32_t);

uint64_t g2_main_mspi_queue_activate_4bfe60(uint32_t controller,
                                              uint32_t increment)
{
    volatile uint8_t *const handle =
        (volatile uint8_t *)(uintptr_t)controller;
    const uint32_t saved = g2_main_critical_save_473940();
    volatile uint32_t *const active =
        (volatile uint32_t *)(void *)(handle + 0x840u);
    const uint32_t previous = *active;
    *active = previous + increment;
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");

    uint32_t result = 0u;
    if (previous == 0u) {
        result = (uint32_t)g2_main_mspi_queue_terminate_4bfd6e(
            controller, 0u, 0u, 0u);
        if (result == 0u) {
            *(volatile uint32_t *)(void *)(handle + 0x24u) = 0u;
            const uint32_t module =
                *(volatile uint32_t *)(void *)(handle + 4u);
            volatile uint32_t *const registers =
                (volatile uint32_t *)(uintptr_t)
                (UINT32_C(0x40060000) + module * 0x1000u);
            registers[0x208u / 4u] = 0x40u;
            registers[0x200u / 4u] |= 0x40u;
            handle[0x83cu] = 1u;
            result = (uint32_t)g2_main_mspi_queue_descriptor_4bfdf4(
                controller, 0u, 0u, 0u);
        }
    }
    return ((uint64_t)saved << 32) | result;
}
