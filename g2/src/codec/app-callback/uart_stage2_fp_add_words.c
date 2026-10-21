/* SPDX-License-Identifier: MIT
 * Stock stage2 0x100076c4 and 0x100076f4 binary64 add/sub entries.
 * Their Ghidra void signatures omit the r0/r1 64-bit return from pack.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_fp_unpack_7d2c(
    const uint32_t input[2], uint32_t output[5]);
extern const uint32_t *gx8002_uart_stage2_fp_add_internal_7400(
    const uint32_t left[5], const uint32_t right[5], uint32_t output[5]);
extern uint64_t gx8002_uart_stage2_fp_pack_7b9c(const uint32_t input[5]);

static uint64_t combine(uint32_t left_low, uint32_t left_high,
                        uint32_t right_low, uint32_t right_high,
                        uint32_t invert_right_sign)
{
    uint32_t left_bits[2] = {left_low, left_high};
    uint32_t right_bits[2] = {right_low, right_high};
    uint32_t left[5], right[5], output[5];
    gx8002_uart_stage2_fp_unpack_7d2c(left_bits, left);
    gx8002_uart_stage2_fp_unpack_7d2c(right_bits, right);
    right[1] ^= invert_right_sign;
    const uint32_t *sum = gx8002_uart_stage2_fp_add_internal_7400(
        left, right, output);
    return gx8002_uart_stage2_fp_pack_7b9c(sum);
}

uint64_t gx8002_uart_stage2_fp_add_words_76c4(
    uint32_t left_low, uint32_t left_high,
    uint32_t right_low, uint32_t right_high)
{
    return combine(left_low, left_high, right_low, right_high, 0u);
}

uint64_t gx8002_uart_stage2_fp_sub_words_76f4(
    uint32_t left_low, uint32_t left_high,
    uint32_t right_low, uint32_t right_high)
{
    return combine(left_low, left_high, right_low, right_high, 1u);
}
