/* SPDX-License-Identifier: MIT */

#include "runtime_numeric.h"

__attribute__((used, noinline))
uint32_t open_cfw_bootloader_u64_to_hex(
    uint64_t value,
    char *output,
    uint32_t lowercase
)
{
    char reversed[16];
    uint32_t count = 0U;

    do {
        const uint32_t nibble = (uint32_t)value & 0x0FU;
        reversed[count++] = (char)(
            nibble < 10U
                ? (uint32_t)'0' + nibble
                : (lowercase != 0U ? (uint32_t)'a' : (uint32_t)'A')
                    + nibble - 10U
        );
        value >>= 4U;
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
