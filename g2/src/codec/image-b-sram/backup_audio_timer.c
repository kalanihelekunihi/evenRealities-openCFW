/* SPDX-License-Identifier: MIT
 * Image-B timer 0x10005070 and delay wrappers 0x10005144/0x10005194.
 * The native low/high register read is scaled by 1000 then divided by 1024.
 */
#include <stdint.h>

#ifdef GX8002_IMAGE_B_TIMER_HOST_TEST
extern uint32_t gx8002_image_b_timer_test_read(uint32_t offset);
#define TIMER_READ(offset) gx8002_image_b_timer_test_read(offset)
#else
#define TIMER_READ(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0400000) + (offset)))
#endif

uint64_t gx8002_image_b_time_10005070(void)
{
    uint32_t low = TIMER_READ(0x44u);
    uint32_t high = TIMER_READ(0x48u);
    uint64_t raw = ((uint64_t)high << 32) | low;
    return (raw * UINT64_C(1000)) >> 10;
}

void gx8002_image_b_delay_10005144(uint32_t duration)
{
    uint64_t current = gx8002_image_b_time_10005070();
    uint64_t deadline = current + 1u + duration;
    while (current < deadline) {
        /* Native 0x1000516e..0x10005174, including delay-slot behavior. */
#ifndef GX8002_IMAGE_B_TIMER_HOST_TEST
        __asm__ volatile (
            "movi r3, 50\n"
            "1: mov r0, r0\n"
            "bnezad r3, 1b\n"
            : : : "r3", "memory");
#else
        volatile uint32_t count = 50u;
        while (count != 0u) --count;
#endif
        current = gx8002_image_b_time_10005070();
    }
}

void gx8002_image_b_delay_ms_10005194(uint32_t milliseconds)
{
    gx8002_image_b_delay_10005144(milliseconds * 1000u);
}
