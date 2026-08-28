/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_UNSIGNED_DIVISION_H
#define OPENCFW_TOUCH_UNSIGNED_DIVISION_H

#include <stdint.h>

typedef struct open_cfw_touch_unsigned_divmod_result {
    uint32_t quotient;
    uint32_t remainder;
} open_cfw_touch_unsigned_divmod_result;

open_cfw_touch_unsigned_divmod_result open_cfw_touch_unsigned_divmod(
    uint32_t numerator, uint32_t denominator);

/* ARM EABI compiler-runtime entry points required by freestanding ARMv6-M. */
uint32_t __aeabi_uidiv(uint32_t numerator, uint32_t denominator);
open_cfw_touch_unsigned_divmod_result __aeabi_uidivmod(
    uint32_t numerator, uint32_t denominator);

#endif
