/* SPDX-License-Identifier: MIT
 * Stock stage2 0x10007730 and 0x10007930 binary64 multiply/divide C
 * candidates. Native bodies unpack, operate on five-word significands,
 * and pack to r0/r1. The long division and four-limb product are source C.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_fp_unpack_7d2c(
    const uint32_t input[2], uint32_t output[5]);
extern uint64_t gx8002_uart_stage2_fp_pack_7b9c(const uint32_t input[5]);

static uint64_t product32(uint32_t a, uint32_t b)
{
    uint32_t al = a & 0xffffu, ah = a >> 16;
    uint32_t bl = b & 0xffffu, bh = b >> 16;
    uint64_t low = (uint64_t)(al * bl);
    uint64_t middle = (uint64_t)(al * bh) + (uint64_t)(ah * bl);
    return low + (middle << 16) + ((uint64_t)(ah * bh) << 32);
}

static void product64(uint64_t a, uint64_t b,
                      uint64_t *high, uint64_t *low)
{
    uint32_t al = (uint32_t)a, ah = (uint32_t)(a >> 32);
    uint32_t bl = (uint32_t)b, bh = (uint32_t)(b >> 32);
    uint64_t p00 = product32(al, bl);
    uint64_t p01 = product32(al, bh);
    uint64_t p10 = product32(ah, bl);
    uint64_t p11 = product32(ah, bh);
    uint64_t lower = p00 + (p01 << 32);
    uint64_t carry = lower < p00;
    uint64_t prior = lower;
    lower += p10 << 32;
    carry += lower < prior;
    *low = lower;
    *high = p11 + (p01 >> 32) + (p10 >> 32) + carry;
}

static uint64_t significand(const uint32_t value[5])
{
    return ((uint64_t)value[4] << 32) | value[3];
}

static uint64_t finish(uint32_t sign, int32_t exponent, uint64_t sig)
{
    uint32_t output[5] = {3u, sign, (uint32_t)exponent,
                          (uint32_t)sig, (uint32_t)(sig >> 32)};
    return gx8002_uart_stage2_fp_pack_7b9c(output);
}

static uint64_t special(const uint32_t a[5], const uint32_t b[5],
                        uint32_t operation, uint32_t *handled)
{
    uint32_t sign = a[1] ^ b[1];
    uint32_t output[5] = {0u, sign, 0u, 0u, 0u};
    if (a[0] < 2u) {
        *handled = 1u;
        return gx8002_uart_stage2_fp_pack_7b9c(a);
    }
    if (b[0] < 2u) {
        *handled = 1u;
        return gx8002_uart_stage2_fp_pack_7b9c(b);
    }
    if (operation == 0u) {
        if ((a[0] == 4u && b[0] == 2u) ||
            (a[0] == 2u && b[0] == 4u)) {
            *handled = 1u;
            return gx8002_uart_stage2_fp_pack_7b9c(output);
        }
        if (a[0] == 4u || b[0] == 4u) output[0] = 4u;
        else if (a[0] == 2u || b[0] == 2u) output[0] = 2u;
        else return 0u;
    } else {
        if ((a[0] == 4u && b[0] == 4u) ||
            (a[0] == 2u && b[0] == 2u)) {
            *handled = 1u;
            return gx8002_uart_stage2_fp_pack_7b9c(output);
        }
        if (a[0] == 4u || b[0] == 2u) output[0] = 4u;
        else if (a[0] == 2u || b[0] == 4u) output[0] = 2u;
        else return 0u;
    }
    *handled = 1u;
    return gx8002_uart_stage2_fp_pack_7b9c(output);
}

static void unpack_pair(uint32_t al, uint32_t ah, uint32_t bl, uint32_t bh,
                        uint32_t a[5], uint32_t b[5])
{
    uint32_t aw[2] = {al, ah}, bw[2] = {bl, bh};
    gx8002_uart_stage2_fp_unpack_7d2c(aw, a);
    gx8002_uart_stage2_fp_unpack_7d2c(bw, b);
}

uint64_t gx8002_uart_stage2_fp_mul_7730(
    uint32_t al, uint32_t ah, uint32_t bl, uint32_t bh)
{
    uint32_t a[5], b[5], handled = 0u;
    unpack_pair(al, ah, bl, bh, a, b);
    uint64_t exceptional = special(a, b, 0u, &handled);
    if (handled) return exceptional;
    uint64_t high, low;
    product64(significand(a), significand(b), &high, &low);
    uint64_t result = (high << 4) | (low >> 60);
    result |= (low & ((UINT64_C(1) << 60) - 1u)) != 0u;
    int32_t exponent = (int32_t)a[2] + (int32_t)b[2];
    if (result >= (UINT64_C(1) << 61)) {
        result = (result >> 1) | (result & 1u);
        ++exponent;
    }
    return finish(a[1] ^ b[1], exponent, result);
}

uint64_t gx8002_uart_stage2_fp_div_7930(
    uint32_t al, uint32_t ah, uint32_t bl, uint32_t bh)
{
    uint32_t a[5], b[5], handled = 0u;
    unpack_pair(al, ah, bl, bh, a, b);
    uint64_t exceptional = special(a, b, 1u, &handled);
    if (handled) return exceptional;
    uint64_t numerator = significand(a);
    uint64_t divisor = significand(b);
    uint64_t top = numerator >> 4;
    uint64_t bottom = numerator << 60;
    uint64_t remainder = 0u, quotient = 0u;
    for (int bit = 120; bit >= 0; --bit) {
        uint32_t next = bit >= 64 ?
            (uint32_t)((top >> (bit - 64)) & 1u) :
            (uint32_t)((bottom >> bit) & 1u);
        remainder = (remainder << 1) | next;
        if (remainder >= divisor) {
            remainder -= divisor;
            if (bit < 64) quotient |= UINT64_C(1) << bit;
        }
    }
    quotient |= remainder != 0u;
    int32_t exponent = (int32_t)a[2] - (int32_t)b[2];
    if (quotient < (UINT64_C(1) << 60)) {
        quotient <<= 1;
        --exponent;
    } else if (quotient >= (UINT64_C(1) << 61)) {
        quotient = (quotient >> 1) | (quotient & 1u);
        ++exponent;
    }
    return finish(a[1] ^ b[1], exponent, quotient);
}
