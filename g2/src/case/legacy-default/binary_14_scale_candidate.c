/* SPDX-License-Identifier: MIT
 * Stock 0x0800018c signed quotient/remainder ABI, source-owned divide loop.
 */
#include <stdint.h>

/* Stock 0x0800018C (case_binary_14_divpair) */
static __attribute__((used)) void case_binary_14_divpair(uint32_t dividend_word,
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

__attribute__((naked)) uint32_t case_binary_14_scale(uint32_t dividend_word,
                                                       uint32_t divisor_word)
{
    __asm__ volatile(
        "push {r4, lr}\n"
        "sub sp, #8\n"
        "mov r2, sp\n"
        "add r3, sp, #4\n"
        "bl case_binary_14_divpair\n"
        "ldr r0, [sp, #0]\n"
        "ldr r1, [sp, #4]\n"
        "add sp, #8\n"
        "pop {r4, pc}\n");
}
