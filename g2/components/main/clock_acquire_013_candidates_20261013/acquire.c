/* SPDX-License-Identifier: MIT
 * Main 0x4c3bfc, 0x4c3c60 and 0x4c3cd4 clock acquire classes 0/1/3.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_critical_save_473940(void);
extern uint32_t g2_main_clock_request_480f0c(uint32_t, uint32_t);

static void restore(uint32_t mask)
{
    __asm__ volatile("msr primask, %0" :: "r"(mask) : "memory");
}

uint64_t g2_main_clock_acquire_0_4c3bfc(uint32_t id,
                                          uint32_t unused, uint32_t high)
{
    (void)unused;
    if (g2_main_clock_request_test_4c37a8(0u, (uint8_t)id) == 0u) {
        high = g2_main_critical_save_473940();
        (void)g2_main_clock_request_set_4c37fe(0u, (uint8_t)id, 1u);
        restore(high);
    }
    return (uint64_t)high << 32;
}

uint64_t g2_main_clock_acquire_1_4c3c60(uint32_t id,
                                          uint32_t unused,
                                          uint32_t third, uint32_t high)
{
    (void)unused;
    (void)third;
    if (*(const volatile uint32_t *)(uintptr_t)UINT32_C(0x200001d8) == 0u)
        return ((uint64_t)high << 32) | 7u;
    if (g2_main_clock_request_test_4c37a8(1u, (uint8_t)id) == 0u) {
        high = g2_main_critical_save_473940();
        (void)g2_main_clock_request_set_4c37fe(1u, (uint8_t)id, 1u);
        restore(high);
    }
    return (uint64_t)high << 32;
}

uint64_t g2_main_clock_acquire_3_4c3cd4(uint32_t id,
                                          uint32_t unused,
                                          uint32_t third, uint32_t high)
{
    (void)unused;
    (void)third;
    const uint32_t previous =
        *(const uint32_t *)(uintptr_t)UINT32_C(0x78ee34);
    if (*(const volatile uint32_t *)(uintptr_t)UINT32_C(0x200001dc) == 0u)
        return ((uint64_t)high << 32) | 7u;
    if (g2_main_clock_request_test_4c37a8(3u, (uint8_t)id) == 0u) {
        high = g2_main_critical_save_473940();
        (void)g2_main_clock_request_480f0c(
            0xfu, (previous & UINT32_C(0xfffffff0)) | 10u);
        (void)g2_main_clock_request_set_4c37fe(3u, (uint8_t)id, 1u);
        restore(high);
    }
    return (uint64_t)high << 32;
}
