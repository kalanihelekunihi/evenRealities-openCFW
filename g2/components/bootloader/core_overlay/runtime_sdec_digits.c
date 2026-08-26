/* SPDX-License-Identifier: GPL-3.0-or-later */

#include "runtime_numeric.h"

__attribute__((used, noinline))
uint32_t open_cfw_bootloader_sdec_digits(int64_t value)
{
    uint64_t magnitude = (uint64_t)value;
    if (value < INT64_C(0)) {
        magnitude = UINT64_C(0) - magnitude;
    }
    return open_cfw_bootloader_udec_digits(magnitude);
}
