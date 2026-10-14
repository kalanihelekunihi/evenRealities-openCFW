/* SPDX-License-Identifier: MIT
 * Main clock class 4 acquire and supporting request/timeout helpers.
 */
#include <stdint.h>

#define REQUEST_BITMAP_BASE UINT32_C(0x20073324)
#define CLASS4_TIMEOUT_ACTIVE UINT32_C(0x20074f57)
#define CLASS4_TIMEOUT_SLOT UINT32_C(0x20074264)
#define CLASS4_TIMEOUT_EXPIRED UINT32_C(0x20074f59)

extern uint32_t g2_main_critical_save_473940(void);
extern void audio_delay_us_selected(uint32_t);
extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_clock_class4_off_4d391e(uint32_t);
extern uint32_t g2_main_clock_class4_trigger_4d3938(uint32_t);

static void restore(uint32_t mask)
{
    __asm__ volatile("msr primask, %0" :: "r"(mask) : "memory");
}

uint32_t g2_main_clock_popcount_4c3750(uint32_t word)
{
    word -= (word >> 1) & UINT32_C(0x55555555);
    uint32_t pairs = ((word >> 2) & UINT32_C(0x33333333)) +
                     (word & UINT32_C(0x33333333));
    return (((pairs + (pairs >> 4)) & UINT32_C(0x0f0f0f0f)) *
            UINT32_C(0x01010101)) >> 24;
}

uint32_t g2_main_clock_request_count_4c37ca(uint32_t clock_class)
{
    const volatile uint32_t *const row =
        (const volatile uint32_t *)(uintptr_t)
        (REQUEST_BITMAP_BASE + ((uint8_t)clock_class * 8u));
    return (uint8_t)(g2_main_clock_popcount_4c3750(row[0]) +
                     g2_main_clock_popcount_4c3750(row[1]));
}

uint32_t g2_main_clock_timeout_wait_4c387e(uint32_t active,
                                              uint32_t remaining,
                                              uint32_t unused,
                                              uint32_t return_value)
{
    (void)unused;
    volatile uint8_t *const flag = (volatile uint8_t *)(uintptr_t)active;
    volatile uint32_t *const ticks = (volatile uint32_t *)(uintptr_t)remaining;
    while (*ticks != 0u && *flag != 0u) {
        audio_delay_us_selected(10u);
        --*ticks;
    }
    return return_value;
}

uint32_t g2_main_clock_timeout_finish_4c3ef4(uint32_t remaining)
{
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)CLASS4_TIMEOUT_ACTIVE;
    if (*active != 0u) {
        (void)g2_main_clock_timeout_wait_4c387e(
            CLASS4_TIMEOUT_ACTIVE, remaining, 0u, 0u);
        const uint32_t previous = g2_main_critical_save_473940();
        *(volatile uint8_t *)(uintptr_t)CLASS4_TIMEOUT_EXPIRED = 1u;
        *active = 0u;
        *(volatile uint32_t *)(uintptr_t)CLASS4_TIMEOUT_SLOT = 0u;
        restore(previous);
    }
    return 0u;
}

uint32_t g2_main_clock_acquire_4_4c3f2a(uint32_t id)
{
    uint32_t remaining = 1000u;
    uint32_t result = 0u;
    const uint8_t request = (uint8_t)id;
    if (g2_main_clock_request_test_4c37a8(4u, request) == 0u) {
        const uint32_t previous = g2_main_critical_save_473940();
        volatile uint8_t *const active =
            (volatile uint8_t *)(uintptr_t)CLASS4_TIMEOUT_ACTIVE;
        volatile uint32_t *const slot =
            (volatile uint32_t *)(uintptr_t)CLASS4_TIMEOUT_SLOT;
        if (*active != 0u)
            remaining = *(volatile uint32_t *)(uintptr_t)(*slot);
        result = *(volatile uint8_t *)(uintptr_t)UINT32_C(0x20004536) == 0u;
        if (result == 0u) {
            if (g2_main_clock_request_count_4c37ca(4u) == 0u) {
                (void)g2_main_clock_class4_off_4d391e(1u);
                if (*(volatile uint32_t *)(uintptr_t)
                    UINT32_C(0x20074250) != 0u) {
                    result = g2_main_clock_class4_trigger_4d3938(
                        *(volatile uint32_t *)(uintptr_t)
                        UINT32_C(0x20073f30));
                    if (result == 0u && *active == 0u &&
                        *(volatile uint8_t *)(uintptr_t)
                        CLASS4_TIMEOUT_EXPIRED == 0u)
                        *active = 1u;
                    if (result != 0u)
                        (void)g2_main_clock_class4_off_4d391e(0u);
                }
            }
            if (result == 0u)
                (void)g2_main_clock_request_set_4c37fe(4u, request, 1u);
            if (*active != 0u)
                *slot = (uint32_t)(uintptr_t)&remaining;
        }
        restore(previous);
    } else {
        const uint32_t previous = g2_main_critical_save_473940();
        if (*(volatile uint8_t *)(uintptr_t)CLASS4_TIMEOUT_ACTIVE != 0u)
            remaining = *(volatile uint32_t *)(uintptr_t)
                (*(volatile uint32_t *)(uintptr_t)CLASS4_TIMEOUT_SLOT);
        *(volatile uint32_t *)(uintptr_t)CLASS4_TIMEOUT_SLOT =
            (uint32_t)(uintptr_t)&remaining;
        restore(previous);
    }
    (void)g2_main_clock_timeout_finish_4c3ef4(
        (uint32_t)(uintptr_t)&remaining);
    return result;
}
