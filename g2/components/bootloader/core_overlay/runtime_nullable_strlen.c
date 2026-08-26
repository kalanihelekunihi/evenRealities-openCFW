/* SPDX-License-Identifier: GPL-3.0-or-later */

#include "runtime_numeric.h"

__attribute__((used, noinline))
uint32_t open_cfw_bootloader_nullable_strlen(const char *text)
{
    uint32_t length = 0U;
    if (text != (const char *)0) {
        while (*text++ != '\0') {
            ++length;
        }
    }
    return length;
}
