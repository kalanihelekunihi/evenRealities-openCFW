/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102098b4..0x1020995a. Unsigned 64-by-32
 * quotient is written back to the input word pair; the low remainder
 * is returned. Nonzero divisor is a native DIVU precondition.
 * This C candidate uses only 32-bit operations to avoid opaque
 * compiler-generated division helpers.
 */
#include <stdint.h>

uint32_t gx8002_xip_div64_102098b4(uint32_t *words, uint32_t divisor)
{
    const uint32_t dividend_lo = words[0];
    const uint32_t dividend_hi = words[1];
    uint32_t quotient_lo = 0u;
    uint32_t quotient_hi = 0u;
    uint32_t remainder_lo = 0u;
    uint32_t remainder_hi = 0u;
    for (uint32_t bit = 64u; bit != 0u;) {
        --bit;
        const uint32_t input_bit = bit >= 32u ?
            ((dividend_hi >> (bit - 32u)) & 1u) :
            ((dividend_lo >> bit) & 1u);
        remainder_hi = remainder_lo >> 31u;
        remainder_lo = (remainder_lo << 1u) | input_bit;
        if (remainder_hi != 0u || remainder_lo >= divisor) {
            const uint32_t before = remainder_lo;
            remainder_lo -= divisor;
            remainder_hi -= before < divisor ? 1u : 0u;
            if (bit >= 32u) quotient_hi |= UINT32_C(1) << (bit - 32u);
            else quotient_lo |= UINT32_C(1) << bit;
        }
    }
    words[0] = quotient_lo;
    words[1] = quotient_hi;
    return remainder_lo;
}
