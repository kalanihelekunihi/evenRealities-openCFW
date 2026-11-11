/* SPDX-License-Identifier: MIT
 * BINH A stage-1 timer configuration at stock 0x10000e84.
 * The MMIO sequence and clock-frequency arithmetic follow the locked body.
 */
#include <stdint.h>

#define REG32(address) (*(volatile uint32_t *)(uintptr_t)(address))

extern uint32_t gx8002_image_a_stage1_clock_frequency_100006a4(uint32_t);

/* Stock 0x100009cc is the shared unsigned division loop. Its wrappers at
 * 0x10000af8 and 0x10000b04 select quotient and remainder. */
__attribute__((noinline, used, section(".spl_a.divmod")))
uint32_t gx8002_image_a_stage1_divmod_100009cc(uint32_t numerator,
                                                uint32_t denominator,
                                                uint32_t remainder)
{
    if (denominator == 0u)
        return remainder ? numerator : 1u;
    return remainder ? numerator % denominator : numerator / denominator;
}

__attribute__((noinline, used, section(".spl_a.udiv")))
uint32_t gx8002_image_a_stage1_udiv_10000af8(uint32_t numerator,
                                               uint32_t denominator)
{
    return gx8002_image_a_stage1_divmod_100009cc(numerator, denominator, 0u);
}

__attribute__((noinline, used, section(".spl_a.umod")))
uint32_t gx8002_image_a_stage1_umod_10000b04(uint32_t numerator,
                                               uint32_t denominator)
{
    return gx8002_image_a_stage1_divmod_100009cc(numerator, denominator, 1u);
}

__attribute__((used, section(".spl_a.timer_config")))
void gx8002_image_a_stage1_timer_config_10000e84(uint32_t period,
                                                  uint32_t mode)
{
    REG32(UINT32_C(0xa0100004)) = 0u;
    REG32(UINT32_C(0xa0100010)) = 3u;
    if (mode == 0u) {
        uint32_t scaled_period = period << 4;
        uint32_t frequency =
            gx8002_image_a_stage1_clock_frequency_100006a4(17u);
        uint32_t whole = gx8002_image_a_stage1_udiv_10000af8(
            frequency, scaled_period);
        uint32_t rem = gx8002_image_a_stage1_umod_10000b04(
            frequency, scaled_period);
        uint32_t fraction = gx8002_image_a_stage1_udiv_10000af8(
            rem * 100u, scaled_period);
        fraction = gx8002_image_a_stage1_udiv_10000af8(
            fraction << 4, 100u);
        while ((REG32(UINT32_C(0xa010007c)) & 1u) != 0u) {}
        REG32(UINT32_C(0xa010000c)) = 128u;
        REG32(UINT32_C(0xa0100000)) = whole & 255u;
        REG32(UINT32_C(0xa0100004)) = (whole >> 8) & 255u;
        REG32(UINT32_C(0xa01000c0)) = fraction & 255u;
    }
    while ((REG32(UINT32_C(0xa010007c)) & 1u) != 0u) {}
    REG32(UINT32_C(0xa010000c)) = 3u;
    REG32(UINT32_C(0xa0100008)) = 79u;
}
