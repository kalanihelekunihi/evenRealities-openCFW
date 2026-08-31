/* SPDX-License-Identifier: MIT */
/*
 * Freestanding ARC GCC emits __mulsi3 for the QP/C memory-pool arithmetic.
 * The reviewed toolchain image intentionally has no target libgcc archive,
 * so provide the standard unsigned low-word multiply semantics in portable C.
 */

#include <stdint.h>

uint32_t __mulsi3(uint32_t multiplicand, uint32_t multiplier)
{
    uint32_t product = 0U;

    while (multiplier != 0U) {
        if ((multiplier & 1U) != 0U) {
            product += multiplicand;
        }
        multiplicand <<= 1U;
        multiplier >>= 1U;
    }
    return product;
}
