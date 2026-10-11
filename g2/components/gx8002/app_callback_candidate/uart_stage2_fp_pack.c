/* SPDX-License-Identifier: MIT
 * Stock stage2 0x10007b9c software binary64 packer candidate.
 * Native returns low/high words in r0/r1. The five input words are class,
 * sign, unbiased exponent, low and high significand limbs. The finite path
 * follows the stock guard/sticky nearest-even rounding and exponent bounds.
 */
#include <stdint.h>

static uint64_t round_shift_right(uint64_t value, unsigned shift)
{
    if (shift == 0u) return value;
    if (shift > 63u) return 0u;
    uint64_t quotient = value >> shift;
    uint64_t remainder_mask = (UINT64_C(1) << shift) - 1u;
    uint64_t remainder = value & remainder_mask;
    uint64_t halfway = UINT64_C(1) << (shift - 1u);
    if (remainder > halfway ||
        (remainder == halfway && (quotient & 1u) != 0u)) ++quotient;
    return quotient;
}

uint64_t gx8002_uart_stage2_fp_pack_7b9c(const uint32_t input[5])
{
    uint64_t sign = (uint64_t)(input[1] & 1u) << 63;
    uint64_t significand = ((uint64_t)input[4] << 32) | input[3];
    uint32_t cls = input[0];
    if (cls < 2u) {
        uint64_t fraction = (significand >> 8) &
                            ((UINT64_C(1) << 52) - 1u);
        fraction |= UINT64_C(1) << 51;
        return sign | (UINT64_C(0x7ff) << 52) | fraction;
    }
    if (cls == 2u || (significand == 0u && cls != 4u)) return sign;
    if (cls == 4u) return sign | (UINT64_C(0x7ff) << 52);

    int32_t exponent = (int32_t)input[2];
    if (exponent > 1023) return sign | (UINT64_C(0x7ff) << 52);
    if (exponent < -1078) return sign;
    unsigned shift = exponent < -1022 ?
        (unsigned)(8 + (-1022 - exponent)) : 8u;
    uint64_t rounded = round_shift_right(significand, shift);
    if (exponent < -1022) {
        if (rounded >= (UINT64_C(1) << 52))
            return sign | (UINT64_C(1) << 52);
        return sign | rounded;
    }
    if (rounded >= (UINT64_C(1) << 53)) {
        rounded >>= 1;
        ++exponent;
        if (exponent > 1023) return sign | (UINT64_C(0x7ff) << 52);
    }
    return sign | ((uint64_t)(exponent + 1023) << 52) |
           (rounded & ((UINT64_C(1) << 52) - 1u));
}
