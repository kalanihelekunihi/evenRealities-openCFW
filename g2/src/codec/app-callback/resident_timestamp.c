/* SPDX-License-Identifier: MIT
 * Resident 0x1002585c gx8002_clock_time_us and 0x10025930
 * gx8002_clock_time_ms. The two clock words are memory mapped at
 * 0xa0400044/48. The stock helpers at 0x102098b4 and 0x10209aa4
 * perform a 64-bit right shift by 10 and unsigned division by 1000.
 */
#include <stdint.h>

static uint64_t resident_clock_time_us(void)
{
    const volatile uint32_t *const clock_words =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0xa0400044);
    const uint32_t low = clock_words[0];
    const uint32_t high = clock_words[1];
    const uint64_t ticks = ((uint64_t)high << 32) | low;
    return (ticks * UINT64_C(1000)) >> 10;
}

uint64_t gx8002_resident_clock_time_us_2585c(void)
{
    return resident_clock_time_us();
}

/* Source-owned exact unsigned 64/1000 division. A direct C division invokes
 * this toolchain's opaque __udivdi3 object under -nostdlib. */
static uint32_t resident_divide_1000_low32(uint64_t numerator)
{
    uint32_t remainder = 0;
    uint32_t quotient_low = 0;
    for (int bit = 63; bit >= 0; --bit) {
        remainder = (remainder << 1) | (uint32_t)((numerator >> bit) & 1u);
        if (remainder >= 1000u) {
            remainder -= 1000u;
            if (bit < 32) quotient_low |= UINT32_C(1) << bit;
        }
    }
    return quotient_low;
}

uint32_t g2_codec_timestamp(void)
{
    return resident_divide_1000_low32(resident_clock_time_us());
}
