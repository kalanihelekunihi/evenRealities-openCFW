/* SPDX-License-Identifier: MIT
 * Main 0x539b56 queue start and 0x480826 bounded register poll.
 */
#include <stdint.h>

extern void audio_delay_us_selected(uint32_t);

uint32_t g2_main_wait_bits_480826(uint32_t iterations,
                                   uint32_t register_address,
                                   uint32_t mask, uint32_t expected,
                                   uint32_t equal)
{
    const volatile uint32_t *const word =
        (const volatile uint32_t *)(uintptr_t)register_address;
    for (;;) {
        const uint32_t observed = *word & mask;
        if ((equal == 0u && observed != expected) ||
            (equal != 0u && observed == expected))
            return 0u;
        if (iterations == 0u) return 4u;
        audio_delay_us_selected(1u);
        --iterations;
    }
}

uint32_t g2_main_queue_start_539b56(uint32_t queue)
{
    if (queue == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)queue &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01504c30))
        return 2u;
    const uint32_t control =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x400204d8);
    if ((control & UINT32_C(0x20000000)) == 0u)
        return 7u;
    const uint32_t factor =
        (control & UINT32_C(0x00000200)) != 0u ? 0x753u : 1000u;
    const uint32_t timing =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x400204e0);
    const uint32_t iterations = ((timing & 0x3fu) * factor + 11u) / 12u;
    return g2_main_wait_bits_480826(iterations, UINT32_C(0x400204e4),
                                     1u, 1u, 1u);
}
