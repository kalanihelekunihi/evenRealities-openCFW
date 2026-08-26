/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Clean-room C implementation of the bootloader's Arm EABI byte-fill entry.
 */

#include "runtime_aeabi_memset.h"

__attribute__((used, noinline))
void open_cfw_bootloader_aeabi_memset(
    void *destination,
    open_cfw_bootloader_memset_size count,
    int value
)
{
    unsigned char *output = (unsigned char *)destination;
    unsigned char byte = (unsigned char)value;

    while (count != 0U) {
        *output = byte;
        ++output;
        --count;
    }
}
