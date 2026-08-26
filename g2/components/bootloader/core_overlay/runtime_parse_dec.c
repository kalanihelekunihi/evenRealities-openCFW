/* SPDX-License-Identifier: GPL-3.0-or-later */

#include "runtime_numeric.h"

__attribute__((used, noinline))
int32_t open_cfw_bootloader_parse_dec(const char *text, uint32_t *consumed)
{
    const char *cursor = text;
    uint32_t value = 0U;
    uint32_t count = 0U;
    uint32_t negative = 0U;

    if (*cursor == '-') {
        negative = 1U;
        ++cursor;
        ++count;
    }
    while ((uint32_t)(uint8_t)*cursor - (uint32_t)'0' < 10U) {
        value = value * 10U + ((uint32_t)(uint8_t)*cursor - (uint32_t)'0');
        ++cursor;
        ++count;
    }
    if (consumed != (uint32_t *)0) {
        *consumed = count;
    }
    if (negative != 0U) {
        value = 0U - value;
    }
    return (int32_t)value;
}
