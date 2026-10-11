/* SPDX-License-Identifier: MIT
 * Stock UART stage2 0x10007d2c software binary64 unpacker.
 * Output is the five-word internal format consumed by the adjacent soft-FP
 * helpers: class, sign, unbiased exponent, low limb, high limb.
 */
#include <stdint.h>

void gx8002_uart_stage2_fp_unpack_7d2c(const uint32_t input[2],
                                         uint32_t output[5])
{
    uint32_t low = input[0];
    uint32_t high = input[1];
    uint32_t exponent = (high >> 20) & 0x7ffu;
    uint32_t fraction_high = high & 0xfffffu;
    output[1] = high >> 31;
    if (exponent != 0u) {
        if (exponent == 0x7ffu) {
            if (low == 0u && fraction_high == 0u) {
                output[0] = 4u;
            } else {
                output[0] = 0u;
                output[3] = low << 8;
                output[4] = (fraction_high << 8) | (low >> 24);
            }
        } else {
            output[0] = 3u;
            output[2] = exponent - 0x3ffu;
            output[3] = low << 8;
            output[4] = (fraction_high << 8) | (low >> 24) |
                        0x10000000u;
        }
        return;
    }
    if (low == 0u && fraction_high == 0u) {
        output[0] = 2u;
        return;
    }
    uint32_t upper = (fraction_high << 8) | (low >> 24);
    uint32_t lower = low << 8;
    output[0] = 3u;
    int32_t candidate = -0x3ff;
    int32_t result;
    do {
        result = candidate;
        uint32_t carry = lower >> 31;
        lower <<= 1;
        upper = (upper << 1) | carry;
        candidate = result - 1;
    } while (upper < 0x10000000u);
    output[2] = (uint32_t)result;
    output[3] = lower;
    output[4] = upper;
}
