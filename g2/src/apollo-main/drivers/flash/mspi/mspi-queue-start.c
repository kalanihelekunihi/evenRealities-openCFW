/* SPDX-License-Identifier: MIT
 * Main 0x4bfd44: acquire the MSPI queue clock, then enable its queue.
 */
#include <stdint.h>

extern uint32_t g2_main_mspi_clock_acquire_4c44bc(uint32_t, uint32_t);
extern uint32_t g2_main_cq_enable_538e3c(uint32_t *);

uint32_t g2_main_mspi_queue_start_4bfd44(uint32_t controller)
{
    const volatile uint8_t *const handle =
        (const volatile uint8_t *)(uintptr_t)controller;
    const uint32_t module =
        *(const volatile uint32_t *)(const void *)(handle + 4u);
    const uint32_t result = g2_main_mspi_clock_acquire_4c44bc(
        4u, (module + 0x10u) & 0xffu);
    if (result != 0u) return result;
    const uint32_t queue =
        *(const volatile uint32_t *)(const void *)(handle + 0x828u);
    return g2_main_cq_enable_538e3c((uint32_t *)(uintptr_t)queue);
}
