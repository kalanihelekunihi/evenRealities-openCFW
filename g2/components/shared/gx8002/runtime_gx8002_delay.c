/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern uint64_t open_cfw_gx8002_clock_time_us(void);

void open_cfw_gx8002_delay_us(uint32_t usec)
{
    uint64_t now = open_cfw_gx8002_clock_time_us();
    uint64_t deadline = now + usec + UINT64_C(1);
    while (now < deadline) {
        /* Preserve the recovered polling backoff instruction sequence. */
        uint32_t count = 50;
        __asm__ volatile("1: mov r0, r0\n\tbnezad %0, 1b"
                         : "+r"(count) : : "memory");
        now = open_cfw_gx8002_clock_time_us();
    }
}

void open_cfw_gx8002_delay_ms(uint32_t msec)
{
    open_cfw_gx8002_delay_us(msec * 1000u);
}
