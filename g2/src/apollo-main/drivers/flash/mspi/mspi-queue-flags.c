/* SPDX-License-Identifier: MIT
 * Main 0x4bfa10: choose command-queue submission flags.
 */
#include <stdint.h>

uint32_t g2_main_mspi_queue_flags_4bfa10(uint32_t controller,
                                           uint32_t requested)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)controller;
    const uint32_t mode = state[0x838u / 4u];
    if (mode == 1u) {
        state[0x838u / 4u] = 2u;
        return requested | UINT32_C(0x40a0);
    }
    if (mode == 2u) return UINT32_C(0x4000);
    return requested | UINT32_C(0x4080);
}
