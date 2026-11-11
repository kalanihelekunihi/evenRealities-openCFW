/* SPDX-License-Identifier: MIT
 * Stock 0x0800018c signed quotient/remainder ABI, source-owned divide loop.
 */
#include <stdint.h>

/* Stock 0x0800018C (case_binary_14_divpair) */
static void case_binary_14_divpair(uint32_t dividend_word,
                            uint32_t divisor_word, uint32_t *quotient_out,
                            uint32_t *remainder_out)
{
    uint32_t negative_dividend = ((int32_t)dividend_word < 0);
    uint32_t negative_divisor = ((int32_t)divisor_word < 0);
    uint32_t dividend = negative_dividend ? 0u - dividend_word : dividend_word;
    uint32_t divisor = negative_divisor ? 0u - divisor_word : divisor_word;
    uint32_t quotient = 0u;
    for (int shift = 32; shift >= 0; --shift) {
        uint32_t shifted_dividend = shift == 32 ? 0u : dividend >> shift;
        if (shifted_dividend >= divisor) {
            uint32_t subtract = shift == 32 ? 0u : divisor << shift;
            dividend -= subtract;
            quotient += shift == 32 ? 0u : 1u << shift;
        }
    }
    if (negative_dividend != negative_divisor)
        quotient = 0u - quotient;
    if (negative_dividend)
        dividend = 0u - dividend;
    *quotient_out = quotient;
    *remainder_out = dividend;
}

/* Stock returns the quotient in R0 and the remainder in R1; every caller
 * (binary_14_candidate.c, binary_14_read_b_candidate.c) declares a uint32_t
 * result and uses only the quotient. */
uint32_t case_binary_14_scale(uint32_t dividend_word, uint32_t divisor_word)
{
    uint32_t quotient, remainder;
    case_binary_14_divpair(dividend_word, divisor_word, &quotient, &remainder);
    return quotient;
}
