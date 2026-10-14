/* SPDX-License-Identifier: MIT
 * Main 0x4c43ec class 6 release and 0x539a10 queue disable.
 * Queue uninitialization at 0x539944 remains an explicit provider gate.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_clock_request_any_4c377a(uint32_t);
extern uint32_t g2_main_critical_save_473940(void);
extern uint32_t g2_main_queue_uninit_539944(uint32_t);
extern uint64_t g2_main_clock_release_2_4c3e9a(uint32_t, uint32_t,
                                                 uint32_t, uint32_t);
extern uint64_t g2_main_clock_release_3_4c3d28(uint32_t, uint32_t,
                                                 uint32_t);

uint32_t g2_main_queue_disable_539a10(uint32_t queue)
{
    if (queue == 0u ||
        (*(volatile uint32_t *)(uintptr_t)queue & UINT32_C(0x01ffffff)) !=
         UINT32_C(0x01504c30))
        return 2u;
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x400204d8);
    *control &= UINT32_C(0xdfffffff);
    *(volatile uint32_t *)(uintptr_t)queue &= UINT32_C(0xfdffffff);
    return 0u;
}

uint64_t g2_main_clock_release_6_4c43ec(uint32_t id,
                                          uint32_t unused, uint32_t high)
{
    (void)unused;
    if (g2_main_clock_request_test_4c37a8(6u, (uint8_t)id) != 0u) {
        high = g2_main_critical_save_473940();
        (void)g2_main_clock_request_set_4c37fe(6u, (uint8_t)id, 0u);
        if (g2_main_clock_request_any_4c377a(6u) == 0u) {
            *(volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f5b) = 0u;
            volatile uint32_t *const queue =
                (volatile uint32_t *)(uintptr_t)UINT32_C(0x2007425c);
            (void)g2_main_queue_disable_539a10(*queue);
            (void)g2_main_queue_uninit_539944(*queue);
            *queue = 0u;
            if (*(const volatile uint8_t *)(uintptr_t)
                 UINT32_C(0x20073f48) == 0u)
                (void)g2_main_clock_release_2_4c3e9a(0x35u, 0u, 0u, 0u);
            else
                (void)g2_main_clock_release_3_4c3d28(0x35u, 0u, 0u);
        }
        __asm__ volatile("msr primask, %0" :: "r"(high) : "memory");
    }
    return (uint64_t)high << 32;
}
