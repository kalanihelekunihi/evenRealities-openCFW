/* SPDX-License-Identifier: MIT
 * Main 0x4c0644: update the MSPI transmit width field from handle mode.
 */
#include <stdint.h>

uint32_t g2_main_mspi_mode_update_4c0644(uint32_t controller)
{
    const volatile uint8_t *const handle =
        (const volatile uint8_t *)(uintptr_t)controller;
    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    const uint32_t mode = handle[11];
    uint32_t code;
    if (mode < 12u) code = 0u;
    else if (mode < 14u) code = 1u;
    else if (mode < 16u) code = 3u;
    else if (mode < 18u) code = 5u;
    else if (mode < 20u) code = 7u;
    else if (mode < 22u) code = 0u;
    else if (mode < 24u) code = 9u;
    else if (mode < 26u) code = 11u;
    else return 0u;
    volatile uint32_t *const register_word =
        (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + module * 0x1000u + 4u);
    *register_word = (*register_word & ~0xfu) | code;
    return 0u;
}
