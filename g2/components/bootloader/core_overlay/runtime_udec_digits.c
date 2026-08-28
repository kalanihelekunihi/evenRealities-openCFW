/* SPDX-License-Identifier: MIT */

#include "runtime_numeric.h"
#include "runtime_udiv10.h"

__attribute__((used, noinline))
uint32_t open_cfw_bootloader_udec_digits(uint64_t value)
{
    uint32_t digits = 1U;
    while (value != UINT64_C(0)) {
        value = open_cfw_bootloader_udiv10(value);
        if (value != UINT64_C(0)) {
            ++digits;
        }
    }
    return digits;
}
