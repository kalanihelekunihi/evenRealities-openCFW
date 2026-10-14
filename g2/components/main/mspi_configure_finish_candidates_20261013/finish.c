/* SPDX-License-Identifier: MIT
 * Main 0x4c07d0: derive command queue transaction width from serial mode.
 */
#include <stdint.h>

void g2_main_mspi_configure_finish_4c07d0(uint32_t controller)
{
    volatile uint8_t *const handle =
        (volatile uint8_t *)(uintptr_t)controller;
    const uint32_t mode = handle[12];
    uint32_t width;
    if (mode >= 6u && mode <= 9u)
        width = 8u;
    else if (mode >= 10u && mode <= 13u)
        width = 4u;
    else if ((mode >= 14u && mode <= 15u) ||
             (mode >= 18u && mode <= 19u))
        width = 2u;
    else if (mode >= 20u && mode <= 23u)
        width = 1u;
    else
        return;
    *(volatile uint32_t *)(uintptr_t)(controller + 0x8ccu) = width;
}
