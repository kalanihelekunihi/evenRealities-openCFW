/* SPDX-License-Identifier: MIT */

#include "runtime_numeric.h"

__attribute__((used, noinline))
uint32_t open_cfw_bootloader_repeat_char(
    char *output,
    uint32_t character,
    int32_t count
)
{
    uint32_t written = 0U;
    if (count > 0) {
        do {
            if (output != (char *)0) {
                *output++ = (char)character;
            }
            ++written;
            --count;
        } while (count != 0);
    }
    return written;
}
