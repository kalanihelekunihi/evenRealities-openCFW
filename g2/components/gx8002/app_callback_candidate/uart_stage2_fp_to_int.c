/* SPDX-License-Identifier: MIT
 * Stock stage2 0x10007a88: binary64 to saturated signed 32-bit integer.
 * Return is represented as uint32_t to preserve the raw ABI word.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_fp_unpack_7d2c(
    const uint32_t input[2], uint32_t output[5]);

uint32_t gx8002_uart_stage2_fp_to_int_7a88(
    uint32_t low, uint32_t high)
{
    uint32_t input[2] = {low, high};
    uint32_t value[5];
    gx8002_uart_stage2_fp_unpack_7d2c(input, value);
    if (value[0] < 3u) return 0u;
    if (value[0] == 4u) return 0x7fffffffu + (value[1] != 0u);
    int32_t exponent = (int32_t)value[2];
    if (exponent < 0) return 0u;
    if (exponent >= 31) return 0x7fffffffu + (value[1] != 0u);
    uint32_t magnitude;
    if (exponent <= 28) {
        magnitude = value[4] >> (28 - exponent);
    } else {
        magnitude = (value[4] << (exponent - 28)) |
                    (value[3] >> (60 - exponent));
    }
    return value[1] == 0u ? magnitude : 0u - magnitude;
}
