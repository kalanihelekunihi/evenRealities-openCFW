/* SPDX-License-Identifier: MIT
 * Retained software-numeric limb product at stock 0x10007b50.
 * The middle input register is unused by the native body.
 */
#include <stdint.h>

uint32_t gx8002_uart_stage2_fp_limb_product_7b50(
    uint32_t left, uint32_t unused, uint32_t right)
{
    (void)unused;
    uint32_t low = (left & 0x7fffu) * (right & 0x7fffu);
    uint32_t middle = (low >> 16) +
        (right >> 16) * (left & 0x7fffu) +
        (left >> 16) * (right & 0x7fffu);
    return (middle << 16) + (low & 0x7fffu);
}
