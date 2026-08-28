/* SPDX-License-Identifier: MIT */
#include <stdint.h>

typedef union {
    uint64_t value;
    struct { uint32_t low; uint32_t high; } words;
} open_cfw_case_u64;

uint32_t __aeabi_uidiv(uint32_t numerator, uint32_t denominator)
{
    uint32_t quotient = 0U;
    uint32_t remainder = 0U;
    int bit;
    if (denominator == 0U) return 0U;
    for (bit = 31; bit >= 0; --bit) {
        uint32_t carry = remainder >> 31U;
        remainder = (remainder << 1U) | ((numerator >> (uint32_t)bit) & 1U);
        if (carry != 0U || remainder >= denominator) {
            remainder -= denominator;
            quotient |= 1U << (uint32_t)bit;
        }
    }
    return quotient;
}

uint64_t __aeabi_llsl(uint64_t input, int shift)
{
    open_cfw_case_u64 source;
    open_cfw_case_u64 result;
    source.value = input;
    result.words.low = 0U;
    result.words.high = 0U;
    if (shift <= 0) return input;
    if (shift < 32) {
        result.words.low = source.words.low << (uint32_t)shift;
        result.words.high = (source.words.high << (uint32_t)shift) |
            (source.words.low >> (32U - (uint32_t)shift));
    } else if (shift < 64) {
        result.words.high = source.words.low << ((uint32_t)shift - 32U);
    }
    return result.value;
}

uint64_t __aeabi_llsr(uint64_t input, int shift)
{
    open_cfw_case_u64 source;
    open_cfw_case_u64 result;
    source.value = input;
    result.words.low = 0U;
    result.words.high = 0U;
    if (shift <= 0) return input;
    if (shift < 32) {
        result.words.high = source.words.high >> (uint32_t)shift;
        result.words.low = (source.words.low >> (uint32_t)shift) |
            (source.words.high << (32U - (uint32_t)shift));
    } else if (shift < 64) {
        result.words.low = source.words.high >> ((uint32_t)shift - 32U);
    }
    return result.value;
}
