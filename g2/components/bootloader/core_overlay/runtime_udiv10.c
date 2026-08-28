/* SPDX-License-Identifier: MIT */

#include "runtime_udiv10.h"

__attribute__((used, noinline))
uint64_t open_cfw_bootloader_udiv10(uint64_t value)
{
    uint64_t quotient = (value >> 1U) + (value >> 2U);
    uint64_t remainder;

    quotient += quotient >> 4U;
    quotient += quotient >> 8U;
    quotient += quotient >> 16U;
    quotient += quotient >> 32U;
    quotient >>= 3U;
    remainder = value - quotient * UINT64_C(10);
    return quotient + ((remainder + UINT64_C(6)) >> 4U);
}
