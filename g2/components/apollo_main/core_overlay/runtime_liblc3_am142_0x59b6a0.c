/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned AM142 byte-mask return helper at 0x0059b6a0.
 */

#include <stdint.h>

uint32_t open_cfw_runtime_am142_0x0059b6a0(uint32_t value)
{
    return value & 0xffU;
}
