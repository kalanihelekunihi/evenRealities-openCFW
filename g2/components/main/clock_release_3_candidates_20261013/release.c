/* SPDX-License-Identifier: MIT
 * Main 0x4c3d28: class 3 clock request release and last-request pin reset.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_clock_request_any_4c377a(uint32_t);
extern uint32_t g2_main_critical_save_473940(void);
extern uint32_t g2_main_clock_request_480f0c(uint32_t, uint32_t);

uint64_t g2_main_clock_release_3_4c3d28(uint32_t id,
                                          uint32_t unused, uint32_t high)
{
    (void)unused;
    if (g2_main_clock_request_test_4c37a8(3u, (uint8_t)id) != 0u) {
        high = g2_main_critical_save_473940();
        (void)g2_main_clock_request_set_4c37fe(3u, (uint8_t)id, 0u);
        if (g2_main_clock_request_any_4c377a(3u) == 0u) {
            (void)g2_main_clock_request_480f0c(
                0xfu, *(const uint32_t *)(uintptr_t)UINT32_C(0x78ee38));
        }
        __asm__ volatile("msr primask, %0" :: "r"(high) : "memory");
    }
    return (uint64_t)high << 32;
}
