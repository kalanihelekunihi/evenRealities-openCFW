/* SPDX-License-Identifier: MIT
 * Stock stage2 0x10007400: add two five-word internal binary64 values.
 * The fixed zero class object at native literal 0x1000772c points to
 * 0x10008ff8, whose five words are all zero. It packs as the stock quiet NaN.
 */
#include <stdint.h>

static const uint32_t invalid_sum[5] = {0u, 0u, 0u, 0u, 0u};

static uint64_t shr_sticky(uint64_t value, unsigned bits)
{
    if (bits == 0u) return value;
    if (bits >= 64u) return 0u;
    uint64_t discarded = value & ((UINT64_C(1) << bits) - 1u);
    return (value >> bits) | (discarded != 0u);
}

const uint32_t *gx8002_uart_stage2_fp_add_internal_7400(
    const uint32_t left[5], const uint32_t right[5], uint32_t output[5])
{
    if (left[0] < 2u) return left;
    if (right[0] < 2u) return right;
    if (left[0] == 4u) {
        if (right[0] != 4u || left[1] == right[1]) return left;
        return invalid_sum;
    }
    if (right[0] == 4u) return right;
    if (right[0] == 2u) {
        if (left[0] != 2u) return left;
        for (unsigned i = 0; i < 5u; ++i) output[i] = left[i];
        output[1] = left[1] & right[1];
        return output;
    }
    if (left[0] == 2u) return right;

    int32_t exponent_left = (int32_t)left[2];
    int32_t exponent_right = (int32_t)right[2];
    int32_t exponent = exponent_left > exponent_right ?
        exponent_left : exponent_right;
    uint64_t a = ((uint64_t)left[4] << 32) | left[3];
    uint64_t b = ((uint64_t)right[4] << 32) | right[3];
    a = shr_sticky(a, (unsigned)(exponent - exponent_left));
    b = shr_sticky(b, (unsigned)(exponent - exponent_right));

    uint32_t sign;
    uint64_t result;
    if (left[1] == right[1]) {
        sign = left[1];
        result = a + b;
    } else if (a >= b) {
        sign = left[1];
        result = a - b;
    } else {
        sign = right[1];
        result = b - a;
    }
    if (result >= (UINT64_C(1) << 61)) {
        result = (result >> 1) | (result & 1u);
        ++exponent;
    } else if (result != 0u) {
        while (result < (UINT64_C(1) << 60)) {
            result <<= 1;
            --exponent;
        }
    }
    output[0] = 3u;
    output[1] = sign;
    output[2] = (uint32_t)exponent;
    output[3] = (uint32_t)result;
    output[4] = (uint32_t)(result >> 32);
    return output;
}
