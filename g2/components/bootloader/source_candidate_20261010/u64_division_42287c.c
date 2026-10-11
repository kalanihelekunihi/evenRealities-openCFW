/* SPDX-License-Identifier: MIT
 * Source body for stock 0x42287c unsigned 64/64 quotient helper.
 * Input words arrive in R0:R1 (numerator) and R2:R3 (denominator); the
 * 64-bit quotient returns in R0:R1. Stock returns numerator for divisor 0.
 * The bitwise division uses no compiler division runtime and preserves that
 * zero-divisor behavior. It is a semantic C candidate pending a stock oracle.
 */
#include <stdint.h>

__attribute__((noinline)) uint64_t opencfw_provider_42287c(
    uint32_t numerator_low, uint32_t numerator_high,
    uint32_t denominator_low, uint32_t denominator_high)
{
    const uint64_t numerator = ((uint64_t)numerator_high << 32) | numerator_low;
    const uint64_t denominator = ((uint64_t)denominator_high << 32) | denominator_low;
    if (denominator == 0)
        return numerator;

    uint64_t quotient = 0;
    uint64_t remainder = 0;
    for (unsigned bit = 64; bit != 0; --bit) {
        const uint64_t carry = remainder >> 63;
        remainder = (remainder << 1) | ((numerator >> (bit - 1)) & 1u);
        if (carry || remainder >= denominator) {
            remainder -= denominator;
            quotient |= (uint64_t)1 << (bit - 1);
        }
    }
    return quotient;
}
