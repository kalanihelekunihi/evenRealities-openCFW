/* SPDX-License-Identifier: MIT
 * Stock stage2 0x10007a48 binary64 comparator entry over four ABI words.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_fp_unpack_7d2c(
    const uint32_t input[2], uint32_t output[5]);
extern int32_t gx8002_uart_stage2_fp_compare_7e10(
    const uint32_t left[5], const uint32_t right[5]);

int32_t gx8002_uart_stage2_fp_compare_words_7a48(
    uint32_t left_low, uint32_t left_high,
    uint32_t right_low, uint32_t right_high)
{
    uint32_t left_input[2] = {left_low, left_high};
    uint32_t right_input[2] = {right_low, right_high};
    uint32_t left[5];
    uint32_t right[5];
    gx8002_uart_stage2_fp_unpack_7d2c(left_input, left);
    gx8002_uart_stage2_fp_unpack_7d2c(right_input, right);
    if (left[0] > 1u && right[0] > 1u)
        return gx8002_uart_stage2_fp_compare_7e10(left, right);
    return -1;
}
