/* SPDX-License-Identifier: MIT
 * Stock 0x0800a3ba..0x0800a3d2: two's-complement conversion of a 16-bit
 * register sample (sourced inline by case_boot_current_sample, 0x08009f18).
 * A clear bit 15 returns the argument unchanged, including any upper bits.
 */
#include <stdint.h>

/* Stock 0x0800A3BA (case_sign_extend_u16) */
int32_t case_sign_extend_u16(uint32_t value)
{
    int32_t sign;
    if ((value & 0x8000u) != 0u) {
        sign = -1;
        value = (uint16_t)(0x10000u - value);
    } else {
        sign = 1;
    }
    return (int32_t)value * sign;
}
