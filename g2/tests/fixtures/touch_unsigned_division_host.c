/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "runtime_touch_unsigned_division.h"

uint32_t fixture_touch_divide(uint32_t numerator, uint32_t denominator)
{
    return __aeabi_uidiv(numerator, denominator);
}

uint32_t fixture_touch_remainder(uint32_t numerator, uint32_t denominator)
{
    return __aeabi_uidivmod(numerator, denominator).remainder;
}
