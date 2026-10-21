/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x1020a528..0x1020a572. Four-word AAPCS product
 * using 16-bit partial products, matching the stock modulo-2^64 result.
 * No 64-bit multiplication expression is used inside this helper.
 */
#include <stdint.h>

uint64_t __muldi3(uint64_t a, uint64_t b)
{
    const uint32_t a_lo = (uint32_t)a;
    const uint32_t a_hi = (uint32_t)(a >> 32u);
    const uint32_t b_lo = (uint32_t)b;
    const uint32_t b_hi = (uint32_t)(b >> 32u);
    const uint32_t a0 = a_lo & UINT32_C(0xffff);
    const uint32_t a1 = a_lo >> 16u;
    const uint32_t b0 = b_lo & UINT32_C(0xffff);
    const uint32_t b1 = b_lo >> 16u;
    const uint32_t p0 = a0 * b0;
    const uint32_t p1 = a1 * b0;
    const uint32_t p2 = a0 * b1;
    const uint32_t p3 = a1 * b1;
    const uint32_t middle = p1 + p2 + (p0 >> 16u);
    const uint32_t carry = middle < p1 ? UINT32_C(0x10000) : 0u;
    const uint32_t low = (middle << 16u) + (p0 & UINT32_C(0xffff));
    const uint32_t high = p3 + carry + (middle >> 16u) +
        a_lo * b_hi + a_hi * b_lo;
    return ((uint64_t)high << 32u) | low;
}
