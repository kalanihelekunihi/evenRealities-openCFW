/* SPDX-License-Identifier: MIT
 * Main 0x4c4016 and 0x4c420c: clock class 4/5 request release.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_clock_request_any_4c377a(uint32_t);
extern uint32_t g2_main_critical_save_473940(void);
extern void g2_main_clock_class4_off_4d391e(uint32_t);
extern void g2_main_clock_class5_off_4d3952(uint32_t);
extern void g2_main_clock_class5_prepare_off_4d39e4(void);
extern uint32_t g2_main_clock_release_2_4c3e9a(uint32_t);
extern uint32_t g2_main_clock_release_3_4c3d28(uint32_t);

static void restore(uint32_t mask)
{
    __asm__ volatile("msr primask, %0" :: "r"(mask) : "memory");
}

uint32_t g2_main_clock_release_4_4c4016(uint32_t id)
{
    if (g2_main_clock_request_test_4c37a8(4u, (uint8_t)id) != 0u) {
        const uint32_t previous = g2_main_critical_save_473940();
        (void)g2_main_clock_request_set_4c37fe(4u, (uint8_t)id, 0u);
        if (g2_main_clock_request_any_4c377a(4u) == 0u)
            g2_main_clock_class4_off_4d391e(0u);
        restore(previous);
    }
    return 0u;
}

uint32_t g2_main_clock_release_5_4c420c(uint32_t id)
{
    if (g2_main_clock_request_test_4c37a8(5u, (uint8_t)id) != 0u) {
        const uint32_t previous = g2_main_critical_save_473940();
        (void)g2_main_clock_request_set_4c37fe(5u, (uint8_t)id, 0u);
        if (g2_main_clock_request_any_4c377a(5u) == 0u) {
            if (*(volatile uint32_t *)(uintptr_t)UINT32_C(0x20074254) != 0u) {
                *(volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f5a) = 0u;
                g2_main_clock_class5_prepare_off_4d39e4();
                (void)g2_main_clock_release_2_4c3e9a(0x36u);
                (void)g2_main_clock_release_3_4c3d28(0x36u);
                *(volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f58) = 0u;
                *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20074268) = 0u;
            }
            g2_main_clock_class5_off_4d3952(0u);
        }
        restore(previous);
    }
    return 0u;
}
