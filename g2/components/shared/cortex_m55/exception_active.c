/* SPDX-License-Identifier: MIT */
/* Stock 0x00442228 tests the complete IPSR value, including IRQ numbers
 * above 31. The decompiler's truncated mask is not the instruction's ABI. */
#include <stdint.h>
#include <stdbool.h>
#include "cmsis_gcc.h"

bool FUN_00442228(void)
{
    return __get_IPSR() != 0U;
}
