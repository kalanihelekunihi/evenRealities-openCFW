/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Clean-room C implementation of the bootloader's Arm EABI forward copy.
 */

#include "runtime_aeabi_memcpy.h"

__attribute__((used, noinline))
void open_cfw_bootloader_aeabi_memcpy(
    void *destination,
    const void *source,
    open_cfw_bootloader_memcpy_size count
)
{
    unsigned char *output = (unsigned char *)destination;
    const unsigned char *input = (const unsigned char *)source;

    while (count != 0U) {
        *output = *input;
        ++output;
        ++input;
        --count;
    }
}
