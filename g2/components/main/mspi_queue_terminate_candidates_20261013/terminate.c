/* SPDX-License-Identifier: MIT
 * Main 0x4bfd6e: terminate MSPI command queue and wait for idle.
 */
#include <stdint.h>

extern void audio_delay_us_selected(uint32_t);
extern uint32_t g2_main_wait_bits_480826(uint32_t, uint32_t,
                                          uint32_t, uint32_t, uint32_t);

uint64_t g2_main_mspi_queue_terminate_4bfd6e(uint32_t controller,
                                               uint32_t second,
                                               uint32_t third,
                                               uint32_t high)
{
    (void)second;
    (void)third;
    const uint32_t module =
        *(const volatile uint32_t *)(uintptr_t)(controller + 4u);
    const uint32_t base = UINT32_C(0x40060000) + module * 0x1000u;
    *(volatile uint32_t *)(uintptr_t)(base + 0x2b4u) =
        UINT32_C(0x00800000);
    uint32_t remaining = 100000u;
    for (;;) {
        const uint32_t status =
            *(const volatile uint32_t *)(uintptr_t)(base + 0x2a0u);
        if ((status & 1u) == 0u) break;
        const uint32_t completion =
            *(const volatile uint32_t *)(uintptr_t)(base + 0x2acu);
        if ((completion & 8u) != 0u &&
            (*(const volatile uint32_t *)(uintptr_t)(base + 0x2b8u) &
             0x80u) != 0u)
            break;
        if (remaining == 0u)
            return ((uint64_t)high << 32) | 4u;
        audio_delay_us_selected(1u);
        --remaining;
    }
    const uint32_t result = g2_main_wait_bits_480826(
        100000u, base + 0x104u, 1u, 0u, 1u);
    return (UINT64_C(1) << 32) | result;
}
