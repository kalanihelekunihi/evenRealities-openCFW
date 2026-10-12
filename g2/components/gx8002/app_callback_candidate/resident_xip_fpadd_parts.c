/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10209dd8..0x1020a096. Five-word soft-float
 * addition, including NaN/Inf/zero early returns, sticky alignment,
 * sign subtraction, normalization, and overflow shift. The static
 * opposite-infinity NaN parts are source-owned stock zeros referenced
 * through the native 0x1020a104 literal (0x1020bd08).
 * Native execution and final target ABI equivalence remain unqualified.
 */
#include <stdint.h>

static const uint32_t opposite_infinity_nan_parts[5] = {0u, 0u, 0u, 0u, 0u};

static uint64_t join_parts(const uint32_t *parts)
{
    return ((uint64_t)parts[4] << 32u) | parts[3];
}

static void write_parts(uint32_t *parts, uint32_t sign,
                        int32_t exponent, uint64_t mantissa)
{
    parts[0] = 3u;
    parts[1] = sign;
    parts[2] = (uint32_t)exponent;
    parts[3] = (uint32_t)mantissa;
    parts[4] = (uint32_t)(mantissa >> 32u);
}

static uint64_t align_sticky(uint64_t mantissa, uint32_t shift)
{
    if (shift >= 64u) return 0u;
    if (shift == 0u) return mantissa;
    const uint64_t lost = mantissa & ((UINT64_C(1) << shift) - 1u);
    return (mantissa >> shift) | (lost != 0u ? 1u : 0u);
}

const uint32_t *gx8002_xip_fpadd_parts_10209dd8(
    const uint32_t first[5], const uint32_t second[5], uint32_t result[5])
{
    if (first[0] < 2u) return first;
    if (second[0] < 2u) return second;
    if (first[0] == 4u) {
        if (second[0] != 4u || first[1] == second[1]) return first;
        return opposite_infinity_nan_parts;
    }
    if (second[0] == 4u) return second;
    if (second[0] == 2u) {
        if (first[0] != 2u) return first;
        result[0] = 2u;
        result[1] = first[1] & second[1];
        result[2] = first[2];
        result[3] = first[3];
        result[4] = first[4];
        return result;
    }
    if (first[0] == 2u) return second;

    int32_t exponent = (int32_t)first[2];
    uint64_t first_mantissa = join_parts(first);
    uint64_t second_mantissa = join_parts(second);
    const int32_t other_exponent = (int32_t)second[2];
    if (exponent > other_exponent) {
        second_mantissa = align_sticky(
            second_mantissa, (uint32_t)(exponent - other_exponent));
    } else if (other_exponent > exponent) {
        first_mantissa = align_sticky(
            first_mantissa, (uint32_t)(other_exponent - exponent));
        exponent = other_exponent;
    }

    uint32_t sign;
    uint64_t mantissa;
    if (first[1] == second[1]) {
        sign = first[1];
        mantissa = first_mantissa + second_mantissa;
    } else if (first_mantissa >= second_mantissa) {
        sign = first[1];
        mantissa = first_mantissa - second_mantissa;
    } else {
        sign = second[1];
        mantissa = second_mantissa - first_mantissa;
    }

    if (mantissa != 0u && (mantissa >> 32u) < UINT32_C(0x10000000)) {
        do {
            mantissa <<= 1u;
            --exponent;
        } while ((mantissa >> 32u) < UINT32_C(0x10000000));
    }
    if ((mantissa >> 32u) > UINT32_C(0x1fffffff)) {
        mantissa = (mantissa >> 1u) | (mantissa & 1u);
        ++exponent;
    }
    write_parts(result, sign, exponent, mantissa);
    return result;
}
