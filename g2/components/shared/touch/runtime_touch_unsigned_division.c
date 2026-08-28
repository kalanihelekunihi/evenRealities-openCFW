/*
 * SPDX-License-Identifier: MIT
 *
 * Constant-iteration unsigned division for the freestanding Touch image.
 * This avoids depending on an unavailable proprietary compiler runtime.
 */
#include "runtime_touch_unsigned_division.h"

open_cfw_touch_unsigned_divmod_result open_cfw_touch_unsigned_divmod(
    uint32_t numerator, uint32_t denominator)
{
    open_cfw_touch_unsigned_divmod_result result = {0U, numerator};
    uint32_t bit;

    if (denominator == 0U) {
        return result;
    }
    result.remainder = 0U;
    for (bit = 32U; bit != 0U; --bit) {
        uint32_t incoming = (numerator >> (bit - 1U)) & 1U;
        uint32_t high = result.remainder >> 31U;
        result.remainder = (result.remainder << 1U) | incoming;
        if (high != 0U || result.remainder >= denominator) {
            result.remainder -= denominator;
            result.quotient |= UINT32_C(1) << (bit - 1U);
        }
    }
    return result;
}

uint32_t __aeabi_uidiv(uint32_t numerator, uint32_t denominator)
{
    return open_cfw_touch_unsigned_divmod(numerator, denominator).quotient;
}

open_cfw_touch_unsigned_divmod_result __aeabi_uidivmod(
    uint32_t numerator, uint32_t denominator)
{
    return open_cfw_touch_unsigned_divmod(numerator, denominator);
}
