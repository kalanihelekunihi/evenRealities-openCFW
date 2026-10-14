/* SPDX-License-Identifier: MIT
 * Main 0x4c4058: finish class 5 timeout and clear its SRAM lease.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_timeout_wait_4c387e(uint32_t, uint32_t,
                                                     uint32_t, uint32_t);
extern uint32_t g2_main_critical_save_473940(void);

uint32_t g2_main_clock_class5_finish_4c4058(uint32_t remaining)
{
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f58);
    if (*active != 0u) {
        (void)g2_main_clock_timeout_wait_4c387e(
            UINT32_C(0x20074f58), remaining, 0u, 0u);
        const uint32_t previous = g2_main_critical_save_473940();
        *active = 0u;
        *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20074268) = 0u;
        __asm__ volatile("msr primask, %0" :: "r"(previous) : "memory");
        return previous;
    }
    return 0u;
}
