/* SPDX-License-Identifier: MIT
 * Main 0x4c427e: class 6 clock and command queue acquisition.
 * Queue lifecycle providers are kept as explicit dependencies.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_clock_request_count_4c37ca(uint32_t);
extern uint32_t g2_main_critical_save_473940(void);
extern uint32_t g2_main_clock_acquire_2_4c3d9e(uint32_t);
extern uint32_t g2_main_clock_acquire_3_4c3cd4(uint32_t);
extern uint32_t g2_main_clock_release_2_4c3e9a(uint32_t);
extern uint32_t g2_main_clock_release_3_4c3d28(uint32_t);
extern uint32_t g2_main_queue_init_5398e0(uint32_t, volatile uint32_t *);
extern uint32_t g2_main_queue_config_539a40(uint32_t, const void *);
extern uint32_t g2_main_queue_enable_539994(uint32_t);
extern uint32_t g2_main_queue_uninit_539944(uint32_t);
extern uint32_t g2_main_queue_start_539b56(uint32_t);

static void restore(uint32_t mask)
{
    __asm__ volatile("msr primask, %0" :: "r"(mask) : "memory");
}

uint64_t g2_main_clock_acquire_6_4c427e(uint32_t id,
                                          uint32_t unused, uint32_t high)
{
    (void)unused;
    uint32_t status = 0u;
    if (g2_main_clock_request_test_4c37a8(6u, (uint8_t)id) != 0u)
        return (uint64_t)high << 32;

    uint32_t saved = g2_main_critical_save_473940();
    if (g2_main_clock_request_count_4c37ca(6u) == 0u)
        *(volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f5b) = 1u;
    (void)g2_main_clock_request_set_4c37fe(6u, (uint8_t)id, 1u);
    restore(saved);

    const uint8_t clock_requested =
        *(const volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f55);
    const uint8_t clock_mode =
        *(const volatile uint8_t *)(uintptr_t)UINT32_C(0x20073f48);
    if (clock_requested != 0u) {
        if (clock_mode == 0u) {
            status = g2_main_clock_acquire_2_4c3d9e(0x35u);
            (void)g2_main_clock_acquire_3_4c3cd4(0x35u);
        } else {
            status = g2_main_clock_acquire_3_4c3cd4(0x35u);
            (void)g2_main_clock_acquire_2_4c3d9e(0x35u);
        }
    }

    saved = g2_main_critical_save_473940();
    uint8_t start_queue = 0u;
    if (status == 0u) {
        if (clock_requested == 0u)
            status = 1u;
        if (status == 0u &&
            *(volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f5b) != 0u) {
            *(volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f5b) = 0u;
            volatile uint32_t *const queue =
                (volatile uint32_t *)(uintptr_t)UINT32_C(0x2007425c);
            if (*queue == 0u)
                status = g2_main_queue_init_5398e0(0u, queue);
            if (status == 0u)
                status = g2_main_queue_config_539a40(
                    *queue, (const void *)(uintptr_t)UINT32_C(0x20073f48));
            if (status == 0u)
                status = g2_main_queue_enable_539994(*queue);
            if (status == 0u)
                start_queue = 1u;
            else if (*queue != 0u) {
                (void)g2_main_queue_uninit_539944(*queue);
                *queue = 0u;
            }
        }
        if (status != 0u)
            (void)g2_main_clock_request_set_4c37fe(6u, (uint8_t)id, 0u);
    } else {
        (void)g2_main_clock_request_set_4c37fe(6u, (uint8_t)id, 0u);
    }
    restore(saved);

    if (clock_requested != 0u) {
        if (status == 0u) {
            if (clock_mode == 0u)
                (void)g2_main_clock_release_3_4c3d28(0x35u);
            else
                (void)g2_main_clock_release_2_4c3e9a(0x35u);
        } else {
            (void)g2_main_clock_release_2_4c3e9a(0x35u);
            (void)g2_main_clock_release_3_4c3d28(0x35u);
        }
    }
    if (start_queue != 0u)
        status = g2_main_queue_start_539b56(
            *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x2007425c));
    return ((uint64_t)saved << 32) | status;
}
