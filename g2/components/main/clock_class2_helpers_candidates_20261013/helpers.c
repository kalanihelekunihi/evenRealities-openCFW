/* SPDX-License-Identifier: MIT
 * Main 0x480c56 clock mode read and 0x4c3d70 pending timeout cleanup.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_timeout_wait_4c387e(uint32_t, uint32_t,
                                                    uint32_t, uint32_t);
extern uint32_t g2_main_critical_save_473940(void);

uint32_t g2_main_clock_mode_read_480c56(uint8_t *mode)
{
    const uint32_t control =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x4002012c);
    *mode = (control & UINT32_C(0x00000100)) != 0u ? 2u :
            (control & 1u) != 0u ? 1u : 0u;
    return 0u;
}

uint64_t g2_main_clock_timeout_cleanup_4c3d70(uint32_t remaining,
                                                uint32_t unused,
                                                uint32_t low,
                                                uint32_t high)
{
    (void)unused;
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f56);
    if (*active != 0u) {
        (void)g2_main_clock_timeout_wait_4c387e(
            UINT32_C(0x20074f56), remaining, 0u, 0u);
        low = g2_main_critical_save_473940();
        *active = 0u;
        *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20074260) = 0u;
        __asm__ volatile("msr primask, %0" :: "r"(low) : "memory");
    }
    return ((uint64_t)high << 32) | low;
}
