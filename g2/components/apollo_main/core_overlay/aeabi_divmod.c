/*
 * SPDX-License-Identifier: MIT
 *
 * Division-free ARM EABI 64-bit signed and unsigned division/modulo
 * reimplementation matched to stock entries 0x0047CC1C and 0x0047CC60.
 *
 * The portable cores use restoring binary long division.  The target-only
 * wrappers marshal the non-C ARM EABI result convention:
 *
 *   input:    r0:r1 dividend, r2:r3 divisor
 *   output:   r0:r1 quotient, r2:r3 remainder
 */

typedef __UINT64_TYPE__ open_cfw_aeabi_divmod_u64;

#ifndef OPEN_CFW_AEABI_DIVMOD_RESULT_DEFINED
#define OPEN_CFW_AEABI_DIVMOD_RESULT_DEFINED
struct open_cfw_aeabi_divmod_result {
    unsigned int quotient_low;
    unsigned int quotient_high;
    unsigned int remainder_low;
    unsigned int remainder_high;
};
#endif

static __attribute__((always_inline)) inline
open_cfw_aeabi_divmod_u64 open_cfw_aeabi_divmod_join(
    unsigned int low,
    unsigned int high
)
{
    return (
        ((open_cfw_aeabi_divmod_u64)high << 32U)
        | (open_cfw_aeabi_divmod_u64)low
    );
}

static __attribute__((always_inline)) inline void
open_cfw_aeabi_divmod_store(
    struct open_cfw_aeabi_divmod_result *result,
    open_cfw_aeabi_divmod_u64 quotient,
    open_cfw_aeabi_divmod_u64 remainder
)
{
    result->quotient_low = (unsigned int)quotient;
    result->quotient_high = (unsigned int)(quotient >> 32U);
    result->remainder_low = (unsigned int)remainder;
    result->remainder_high = (unsigned int)(remainder >> 32U);
}

__attribute__((used, noinline))
void open_cfw_aeabi_uldivmod_core(
    unsigned int dividend_low,
    unsigned int dividend_high,
    unsigned int divisor_low,
    unsigned int divisor_high,
    struct open_cfw_aeabi_divmod_result *result
)
{
    open_cfw_aeabi_divmod_u64 dividend =
        open_cfw_aeabi_divmod_join(dividend_low, dividend_high);
    open_cfw_aeabi_divmod_u64 divisor =
        open_cfw_aeabi_divmod_join(divisor_low, divisor_high);
    open_cfw_aeabi_divmod_u64 quotient = 0U;
    open_cfw_aeabi_divmod_u64 remainder = 0U;
    unsigned int bit;

    if (divisor == 0U) {
        open_cfw_aeabi_divmod_store(result, dividend, 0U);
        return;
    }

#pragma clang loop unroll(disable)
    for (bit = 0U; bit < 64U; ++bit) {
        unsigned int overflow = (unsigned int)(remainder >> 63U);

        remainder = (remainder << 1U) | (dividend >> 63U);
        dividend <<= 1U;
        quotient <<= 1U;
        if (overflow != 0U || remainder >= divisor) {
            remainder -= divisor;
            quotient |= 1U;
        }
    }
    open_cfw_aeabi_divmod_store(result, quotient, remainder);
}

__attribute__((used, noinline))
void open_cfw_aeabi_ldivmod_core(
    unsigned int dividend_low,
    unsigned int dividend_high,
    unsigned int divisor_low,
    unsigned int divisor_high,
    struct open_cfw_aeabi_divmod_result *result
)
{
    open_cfw_aeabi_divmod_u64 dividend =
        open_cfw_aeabi_divmod_join(dividend_low, dividend_high);
    open_cfw_aeabi_divmod_u64 divisor =
        open_cfw_aeabi_divmod_join(divisor_low, divisor_high);
    unsigned int dividend_negative = dividend_high >> 31U;
    unsigned int divisor_negative = divisor_high >> 31U;
    struct open_cfw_aeabi_divmod_result magnitude;
    open_cfw_aeabi_divmod_u64 quotient;
    open_cfw_aeabi_divmod_u64 remainder;

    if (dividend_negative != 0U) {
        dividend = 0U - dividend;
    }
    if (divisor_negative != 0U) {
        divisor = 0U - divisor;
    }

    open_cfw_aeabi_uldivmod_core(
        (unsigned int)dividend,
        (unsigned int)(dividend >> 32U),
        (unsigned int)divisor,
        (unsigned int)(divisor >> 32U),
        &magnitude
    );
    quotient = open_cfw_aeabi_divmod_join(
        magnitude.quotient_low,
        magnitude.quotient_high
    );
    remainder = open_cfw_aeabi_divmod_join(
        magnitude.remainder_low,
        magnitude.remainder_high
    );

    if ((dividend_negative ^ divisor_negative) != 0U) {
        quotient = 0U - quotient;
    }
    if (dividend_negative != 0U) {
        remainder = 0U - remainder;
    }
    open_cfw_aeabi_divmod_store(result, quotient, remainder);
}

#ifndef OPEN_CFW_AEABI_DIVMOD_HOST

__attribute__((used, noinline, naked))
void open_cfw_aeabi_uldivmod(void)
{
    __asm__ volatile(
        "push {r4, lr}\n"
        "sub sp, #24\n"
        "add r4, sp, #4\n"
        "str r4, [sp]\n"
        "bl open_cfw_aeabi_uldivmod_core\n"
        "ldmia r4, {r0, r1, r2, r3}\n"
        "add sp, #24\n"
        "pop {r4, pc}\n"
    );
}

__attribute__((used, noinline, naked))
void open_cfw_aeabi_ldivmod(void)
{
    __asm__ volatile(
        "push {r4, lr}\n"
        "sub sp, #24\n"
        "add r4, sp, #4\n"
        "str r4, [sp]\n"
        "bl open_cfw_aeabi_ldivmod_core\n"
        "ldmia r4, {r0, r1, r2, r3}\n"
        "add sp, #24\n"
        "pop {r4, pc}\n"
    );
}

#endif
