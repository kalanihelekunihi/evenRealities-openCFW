/* SPDX-License-Identifier: MIT
 * Main 0x4c4086: class 5 clock request, power configuration and rollback.
 */
#include <stdint.h>

extern uint32_t g2_main_critical_save_473940(void);
extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_count_4c37ca(uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_clock_acquire_2_4c3d9e(uint32_t);
extern uint32_t g2_main_clock_acquire_3_4c3cd4(uint32_t);
extern uint32_t g2_main_clock_release_2_4c3e9a(uint32_t);
extern uint32_t g2_main_clock_release_3_4c3d28(uint32_t);
extern uint32_t g2_main_clock_class5_off_4d3952(uint32_t);
extern uint32_t g2_main_clock_class5_config_4d3992(uint32_t);
extern uint32_t g2_main_clock_class5_finish_4c4058(uint32_t);

static void restore(uint32_t previous)
{
    __asm__ volatile("msr primask, %0" :: "r"(previous) : "memory");
}

uint32_t g2_main_clock_acquire_5_4c4086(uint32_t id)
{
    const uint8_t request = (uint8_t)id;
    uint32_t remaining = 50u;
    uint32_t result = 0u;
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f58);
    volatile uint32_t *const slot =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20074268);
    volatile uint8_t *const prepared =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f5a);
    volatile uint8_t *const available =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20004537);
    const volatile uint32_t *const context =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x20074254);
    const volatile uint8_t *const mode =
        (const volatile uint8_t *)(uintptr_t)UINT32_C(0x20073f3c);

    if (g2_main_clock_request_test_4c37a8(5u, request) == 0u) {
        uint32_t previous = g2_main_critical_save_473940();
        if (g2_main_clock_request_count_4c37ca(5u) == 0u)
            *prepared = 1u;
        (void)g2_main_clock_request_set_4c37fe(5u, request, 1u);
        restore(previous);

        if (*available != 0u && *context != 0u) {
            result = *mode == 0u ?
                g2_main_clock_acquire_2_4c3d9e(0x36u) :
                g2_main_clock_acquire_3_4c3cd4(0x36u);
            if (result != 0u) {
                previous = g2_main_critical_save_473940();
                (void)g2_main_clock_request_set_4c37fe(
                    5u, request, 0u);
                restore(previous);
            }
        }

        if (result == 0u) {
            previous = g2_main_critical_save_473940();
            if (*active != 0u)
                remaining = *(volatile uint32_t *)(uintptr_t)(*slot);
            if (*available == 0u)
                result = 1u;
            if (result == 0u && *prepared != 0u) {
                *prepared = 0u;
                (void)g2_main_clock_class5_off_4d3952(1u);
                if (*context != 0u) {
                    result = g2_main_clock_class5_config_4d3992(
                        UINT32_C(0x20073f3c));
                    if (result == 0u && *active == 0u)
                        *active = 1u;
                    if (result != 0u)
                        (void)g2_main_clock_class5_off_4d3952(0u);
                }
            }
            if (result != 0u)
                (void)g2_main_clock_request_set_4c37fe(
                    5u, request, 0u);
            if (*active != 0u)
                *slot = (uint32_t)(uintptr_t)&remaining;
            restore(previous);
        }
        if (result != 0u && *available != 0u && *context != 0u) {
            result = *mode == 0u ?
                g2_main_clock_release_2_4c3e9a(0x36u) :
                g2_main_clock_release_3_4c3d28(0x36u);
        }
    } else {
        const uint32_t previous = g2_main_critical_save_473940();
        if (*active != 0u)
            remaining = *(volatile uint32_t *)(uintptr_t)(*slot);
        *slot = (uint32_t)(uintptr_t)&remaining;
        restore(previous);
    }
    (void)g2_main_clock_class5_finish_4c4058(
        (uint32_t)(uintptr_t)&remaining);
    return result;
}
