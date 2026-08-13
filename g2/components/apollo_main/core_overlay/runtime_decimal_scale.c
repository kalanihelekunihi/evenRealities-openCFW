/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 decimal-scaling helper at
 * 0x0048262C. The exact stock boundary, two callers, non-negative exponent
 * contract, and multiplication dependency are recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_decimal_scale_uintptr;

typedef double (*open_cfw_decimal_scale_multiply_function)(
    double left,
    double right
);

#ifndef OPEN_CFW_DECIMAL_SCALE_MULTIPLY
#define OPEN_CFW_DECIMAL_SCALE_MULTIPLY(left, right) \
    (((open_cfw_decimal_scale_multiply_function) \
        (open_cfw_decimal_scale_uintptr)0x004D4355U)((left), (right)))
#endif

/*
 * Both reviewed callers normalize the exponent to the non-negative magnitude
 * of their decimal adjustment before entering this helper. Preserve the
 * stock signed arithmetic shift so an accidental negative input retains the
 * original out-of-contract behavior instead of silently becoming unsigned.
 */
__attribute__((used, noinline))
double open_cfw_decimal_scale(double value, int exponent)
{
    double factor = 10.0;

    while (exponent != 0) {
        if ((exponent & 1) != 0) {
            value = OPEN_CFW_DECIMAL_SCALE_MULTIPLY(value, factor);
        }
        factor = OPEN_CFW_DECIMAL_SCALE_MULTIPLY(factor, factor);
        exponent >>= 1;
    }

    return value;
}

#undef OPEN_CFW_DECIMAL_SCALE_MULTIPLY
