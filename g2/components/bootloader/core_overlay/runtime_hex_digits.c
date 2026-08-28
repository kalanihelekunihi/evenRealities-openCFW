/* SPDX-License-Identifier: MIT */

#include "runtime_numeric.h"

__attribute__((used, noinline))
uint32_t open_cfw_bootloader_hex_digits(uint64_t value)
{
    uint32_t digits = 1U;
    while (value >= UINT64_C(16)) {
        value >>= 4U;
        ++digits;
    }
    return digits;
}
