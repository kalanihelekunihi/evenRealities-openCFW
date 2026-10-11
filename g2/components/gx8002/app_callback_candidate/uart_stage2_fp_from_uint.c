/* SPDX-License-Identifier: MIT
 * Stock stage2 0x10007af8: unsigned 32-bit integer to binary64 words.
 * The native leading-zero count places the highest input bit at internal
 * significand bit 60 before its call to the five-word packer.
 */
#include <stdint.h>

extern uint64_t gx8002_uart_stage2_fp_pack_7b9c(const uint32_t input[5]);

uint64_t gx8002_uart_stage2_fp_from_uint_7af8(uint32_t value)
{
    uint32_t internal[5] = {0u, 0u, 0u, 0u, 0u};
    if (value == 0u) {
        internal[0] = 2u;
    } else {
        unsigned exponent = 31u;
        while ((value & (UINT32_C(1) << exponent)) == 0u) --exponent;
        uint64_t significand = (uint64_t)value << (60u - exponent);
        internal[0] = 3u;
        internal[2] = exponent;
        internal[3] = (uint32_t)significand;
        internal[4] = (uint32_t)(significand >> 32);
    }
    return gx8002_uart_stage2_fp_pack_7b9c(internal);
}
