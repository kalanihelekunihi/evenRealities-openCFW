/* SPDX-License-Identifier: MIT
 * Main 0x4c3e9a: class 2 clock release, including the mode-4 shutdown
 * register sequence observed through native 0x4809c4.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_clock_request_any_4c377a(uint32_t);
extern uint32_t g2_main_critical_save_473940(void);

uint64_t g2_main_clock_release_2_4c3e9a(uint32_t id,
                                          uint32_t unused, uint32_t high,
                                          uint32_t fourth)
{
    (void)unused;
    (void)fourth;
    if (g2_main_clock_request_test_4c37a8(2u, (uint8_t)id) != 0u) {
        const uint32_t saved = g2_main_critical_save_473940();
        (void)g2_main_clock_request_set_4c37fe(2u, (uint8_t)id, 0u);
        if (g2_main_clock_request_any_4c377a(2u) == 0u) {
            high = (high & UINT32_C(0xffffff00)) | 1u;
            volatile uint32_t *const clock_config =
                (volatile uint32_t *)(uintptr_t)UINT32_C(0x40020128);
            volatile uint32_t *const clock_control =
                (volatile uint32_t *)(uintptr_t)UINT32_C(0x4002012c);
            const uint32_t mux =
                *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x200001e0);
            const uint32_t div =
                *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x200001e4);
            *clock_config = (*clock_config & UINT32_C(0xc0007000)) |
                            (mux & 0x3fu) | ((div & 0xfu) << 6) |
                            UINT32_C(0x03118000);
            *clock_control = (*clock_control & UINT32_C(0xfffffed4)) | 2u;
            *(volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f56) = 0u;
            *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20074260) = 0u;
        }
        __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
    }
    return (uint64_t)high << 32;
}
