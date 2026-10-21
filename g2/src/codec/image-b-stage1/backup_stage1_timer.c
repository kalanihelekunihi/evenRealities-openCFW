/* SPDX-License-Identifier: MIT
 * BINH-B stage1 0x10001260 timer setup, corrected runtime PC.
 * The general clock-frequency query remains a genuine child contract.
 */
#include <stdint.h>

#define REG32(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern uint32_t gx8002_image_b_stage1_clock_frequency_10000300(uint32_t module);

/* Native software-division leaves 0x10000e20 and 0x10000e64.
 * On zero divisor their instruction sequence yields 1 and numerator.
 */
uint32_t gx8002_image_b_stage1_udiv_10000e20(uint32_t num, uint32_t den)
{
    return den ? num / den : 1u;
}

uint32_t gx8002_image_b_stage1_umod_10000e64(uint32_t num, uint32_t den)
{
    return den ? num % den : num;
}

void gx8002_image_b_stage1_timer_config_10001260(uint32_t period, uint32_t mode)
{
    REG32(0xa0100004u) = 0;
    REG32(0xa0100010u) = 3;
    if (mode == 0u) {
        uint32_t scaled_period = period << 4;
        uint32_t frequency = gx8002_image_b_stage1_clock_frequency_10000300(17u);
        uint32_t whole = gx8002_image_b_stage1_udiv_10000e20(frequency, scaled_period);
        uint32_t rem = gx8002_image_b_stage1_umod_10000e64(frequency, scaled_period);
        uint32_t fraction = gx8002_image_b_stage1_udiv_10000e20(rem * 100u, scaled_period);
        fraction = gx8002_image_b_stage1_udiv_10000e20(fraction << 4, 100u);
        while (REG32(0xa010007cu) & 1u) {}
        REG32(0xa010000cu) = 128u;
        REG32(0xa0100000u) = whole & 255u;
        REG32(0xa0100004u) = (whole >> 8) & 255u;
        REG32(0xa01000c0u) = fraction & 255u;
    }
    while (REG32(0xa010007cu) & 1u) {}
    REG32(0xa010000cu) = 3u;
    REG32(0xa0100008u) = 79u;
}
