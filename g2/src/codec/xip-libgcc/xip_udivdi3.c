/* SPDX-License-Identifier: MIT
 * Stock image-A XIP 0x10209aa4..0x10209dd8 (gx8002_udivdi3, toolchain
 * libgcc __udivdi3). The inventory row 0x10209c74 is an interior
 * instruction boundary of this body (the normalised d1 != 0 quotient
 * path), not a separate function. Literal pool word 0x10209dd4 holds the
 * bit-length table address 0x1020bd1c.
 *
 * Unsigned 64/64 division by two-digit (base 2^16) long division on
 * normalised 32-bit limbs; leading zeros come from the 256-entry bit
 * length table. The pinned C-SKY GCC 6.3 ck803/hard-fp libgcc.a
 * _udivdi3.o is byte-identical to stock modulo relocations.
 */
#include <stdint.h>

/* ROM 0x1020bd1c: bit length of each byte value (resident_xip_udiv_bitlength_data.c). */
extern const uint8_t gx8002_xip_udivdi3_bit_length_1020bd1c[256];

static uint32_t leading_zeros(uint32_t value)
{
    uint32_t shift;
    if (value < UINT32_C(0x10000))
        shift = value < UINT32_C(0x100) ? 0u : 8u;
    else
        shift = value <= UINT32_C(0xffffff) ? 16u : 24u;
    return 32u - (gx8002_xip_udivdi3_bit_length_1020bd1c[value >> shift] + shift);
}

/* Divide high:low by a normalised divisor (bit 31 set, high < divisor).
 * Quotient digits are corrected at most twice, as in the stock body. */
static uint32_t divide_two_limbs(uint32_t high, uint32_t low, uint32_t divisor,
                                 uint32_t *remainder)
{
    const uint32_t divisor_high = divisor >> 16;
    const uint32_t divisor_low = divisor & UINT32_C(0xffff);

    uint32_t quotient_high = high / divisor_high;
    uint32_t partial = high - quotient_high * divisor_high;
    uint32_t product = quotient_high * divisor_low;
    partial = (partial << 16) | (low >> 16);
    if (partial < product) {
        --quotient_high;
        partial += divisor;
        if (partial >= divisor && partial < product) {
            --quotient_high;
            partial += divisor;
        }
    }
    partial -= product;

    uint32_t quotient_low = partial / divisor_high;
    uint32_t rest = partial - quotient_low * divisor_high;
    product = quotient_low * divisor_low;
    rest = (rest << 16) | (low & UINT32_C(0xffff));
    if (rest < product) {
        --quotient_low;
        rest += divisor;
        if (rest >= divisor && rest < product) {
            --quotient_low;
            rest += divisor;
        }
    }
    *remainder = rest - product;
    return (quotient_high << 16) | quotient_low;
}

/* 32x32 -> 64 product from four 16-bit partial products. */
static void multiply_limbs(uint32_t left, uint32_t right,
                           uint32_t *high, uint32_t *low)
{
    const uint32_t left_low = left & UINT32_C(0xffff);
    const uint32_t left_high = left >> 16;
    const uint32_t right_low = right & UINT32_C(0xffff);
    const uint32_t right_high = right >> 16;
    const uint32_t p0 = left_low * right_low;
    const uint32_t p1 = left_low * right_high;
    const uint32_t p2 = left_high * right_low;
    uint32_t p3 = left_high * right_high;
    uint32_t middle = p1 + (p0 >> 16);
    middle += p2;
    if (middle < p2)
        p3 += UINT32_C(0x10000);
    *high = p3 + (middle >> 16);
    *low = (middle << 16) + (p0 & UINT32_C(0xffff));
}

/* Native 0x10209b98: a zero divisor is replaced by 1/0 on the hardware
 * divider, keeping the stock divide-by-zero behaviour explicit. */
static uint32_t hardware_reciprocal_of_zero(uint32_t zero)
{
    uint32_t result;
    __asm__ volatile("divu %0, %1, %2" : "=r"(result) : "r"(1u), "r"(zero));
    return result;
}

/* Stock 0x10209C74 (gx8002_uart_transmit_dma: interior boundary of this body) */
uint64_t gx8002_udivdi3(uint64_t numerator, uint64_t denominator)
{
    uint32_t n0 = (uint32_t)numerator;
    uint32_t n1 = (uint32_t)(numerator >> 32);
    uint32_t d0 = (uint32_t)denominator;
    uint32_t d1 = (uint32_t)(denominator >> 32);
    uint32_t q0;
    uint32_t q1;
    uint32_t remainder;

    if (d1 == 0u) {
        if (d0 > n1) {
            /* 0q = nn / 0D */
            const uint32_t shift = leading_zeros(d0);
            if (shift != 0u) {
                d0 <<= shift;
                n1 = (n1 << shift) | (n0 >> (32u - shift));
                n0 <<= shift;
            }
            q0 = divide_two_limbs(n1, n0, d0, &remainder);
            q1 = 0u;
        } else {
            /* qq = NN / 0d */
            if (d0 == 0u)
                d0 = hardware_reciprocal_of_zero(d0);
            const uint32_t shift = leading_zeros(d0);
            if (shift == 0u) {
                n1 -= d0;
                q1 = 1u;
            } else {
                const uint32_t back = 32u - shift;
                d0 <<= shift;
                const uint32_t n2 = n1 >> back;
                n1 = (n1 << shift) | (n0 >> back);
                n0 <<= shift;
                q1 = divide_two_limbs(n2, n1, d0, &n1);
            }
            q0 = divide_two_limbs(n1, n0, d0, &remainder);
        }
    } else if (d1 > n1) {
        /* 00 = nn / DD */
        q0 = 0u;
        q1 = 0u;
    } else {
        /* 0q = NN / dd */
        const uint32_t shift = leading_zeros(d1);
        if (shift == 0u) {
            q0 = (n1 > d1 || n0 >= d0) ? 1u : 0u;
        } else {
            const uint32_t back = 32u - shift;
            d1 = (d1 << shift) | (d0 >> back);
            d0 <<= shift;
            const uint32_t n2 = n1 >> back;
            n1 = (n1 << shift) | (n0 >> back);
            n0 <<= shift;
            q0 = divide_two_limbs(n2, n1, d1, &n1);
            uint32_t m1;
            uint32_t m0;
            multiply_limbs(q0, d0, &m1, &m0);
            if (m1 > n1 || (m1 == n1 && m0 > n0))
                --q0;
        }
        q1 = 0u;
    }
    return ((uint64_t)q1 << 32) | q0;
}
