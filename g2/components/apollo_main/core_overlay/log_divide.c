/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the unsigned 64-bit divide-by-ten helper used by
 * the G2 2.2.6.10 logging decimal routines at 0x00472C84.
 */

typedef union {
    unsigned long long value;
    struct {
        unsigned int low;
        unsigned int high;
    } words;
} open_cfw_log_u64_result;

__attribute__((used, noinline))
unsigned long long open_cfw_log_divide_u64_by_10(
    unsigned int low,
    unsigned int high
)
{
    open_cfw_log_u64_result result;
    unsigned int quotient_low = 0U;
    unsigned int quotient_high = 0U;
    unsigned int remainder = 0U;
    unsigned int index;

    /*
     * A fixed 64-step binary division avoids compiler runtime helpers while
     * preserving the stock two-word input and r0/r1 quotient ABI.
     */
    for (index = 0U; index < 64U; index += 1U) {
        unsigned int incoming = high >> 31U;

        high = (high << 1U) | (low >> 31U);
        low <<= 1U;
        quotient_high = (quotient_high << 1U) | (quotient_low >> 31U);
        quotient_low <<= 1U;
        remainder = (remainder << 1U) | incoming;
        if (remainder >= 10U) {
            remainder -= 10U;
            quotient_low |= 1U;
        }
    }
    result.words.low = quotient_low;
    result.words.high = quotient_high;
    return result.value;
}
