/* SPDX-License-Identifier: MIT
 * Main 0x4c3c2e and 0x4c3ca2: class 0/1 clock request release.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_critical_save_473940(void);

static void restore(uint32_t mask)
{
    __asm__ volatile("msr primask, %0" :: "r"(mask) : "memory");
}

static uint64_t release(uint32_t clock_class, uint32_t id, uint32_t high)
{
    if (g2_main_clock_request_test_4c37a8(clock_class, (uint8_t)id) != 0u) {
        high = g2_main_critical_save_473940();
        (void)g2_main_clock_request_set_4c37fe(clock_class, (uint8_t)id, 0u);
        restore(high);
    }
    return (uint64_t)high << 32;
}

uint64_t g2_main_clock_release_0_4c3c2e(uint32_t id,
                                          uint32_t unused, uint32_t high)
{
    (void)unused;
    return release(0u, id, high);
}

uint64_t g2_main_clock_release_1_4c3ca2(uint32_t id,
                                          uint32_t unused, uint32_t high)
{
    (void)unused;
    return release(1u, id, high);
}
