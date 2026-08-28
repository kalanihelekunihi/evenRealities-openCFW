/* SPDX-License-Identifier: MIT */

#include "runtime_numeric.h"
#include "runtime_udiv10.h"

__attribute__((used, noinline))
uint32_t open_cfw_bootloader_u64_to_dec(uint64_t value, char *output)
{
    char reversed[20];
    uint32_t count = 0U;

    do {
        const uint64_t quotient = open_cfw_bootloader_udiv10(value);
        reversed[count++] = (char)('0' + (uint32_t)(value - quotient * 10U));
        value = quotient;
    } while (value != UINT64_C(0));

    if (output != (char *)0) {
        uint32_t remaining = count;
        while (remaining != 0U) {
            --remaining;
            *output++ = reversed[remaining];
        }
        *output = '\0';
    }
    return count;
}
