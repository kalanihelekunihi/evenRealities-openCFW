/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x1020a704 unpack-double and 0x1020a7e8
 * compare-parts C candidates. The five-word part layout and branch
 * cases come from retained stock pseudocode and C-SKY ranges. Native
 * execution and final soft-float ABI equality remain unqualified.
 */
#include <stdint.h>

void gx8002_xip_unpack_double_1020a704(
    const uint32_t input[2], uint32_t parts[5])
{
    const uint32_t low = input[0];
    const uint32_t high = input[1];
    const uint32_t exponent = (high >> 20u) & UINT32_C(0x7ff);
    /* Native zext r12,r12,19,0 keeps all twenty fraction high bits;
     * retained decompilation dropped bit 19. */
    const uint32_t fraction_high = high & UINT32_C(0xfffff);
    parts[1] = high >> 31u;
    if (exponent != 0u) {
        if (exponent == UINT32_C(0x7ff)) {
            if (low == 0u && fraction_high == 0u) {
                parts[0] = 4u;
            } else {
                parts[0] = (fraction_high & UINT32_C(0x80000)) != 0u
                    ? 1u : 0u;
                parts[3] = low << 8u;
                parts[4] = ((fraction_high << 8u) | (low >> 24u)) &
                    ~UINT32_C(0x08000000);
            }
        } else {
            parts[0] = 3u;
            parts[2] = exponent - UINT32_C(0x3ff);
            parts[3] = low << 8u;
            parts[4] = (fraction_high << 8u) | (low >> 24u) |
                UINT32_C(0x10000000);
        }
        return;
    }
    if (low == 0u && fraction_high == 0u) {
        parts[0] = 2u;
        return;
    }
    uint32_t mantissa_high = (fraction_high << 8u) | (low >> 24u);
    uint32_t mantissa_low = low << 8u;
    parts[0] = 3u;
    int32_t current_exponent = -1023;
    int32_t assigned_exponent;
    do {
        assigned_exponent = current_exponent;
        mantissa_high = (mantissa_high << 1u) |
            (mantissa_low >> 31u);
        mantissa_low <<= 1u;
        --current_exponent;
    } while (mantissa_high < UINT32_C(0x10000000));
    parts[2] = (uint32_t)assigned_exponent;
    parts[3] = mantissa_low;
    parts[4] = mantissa_high;
}

int32_t gx8002_xip_fpcmp_parts_1020a7e8(
    const uint32_t first[5], const uint32_t second[5])
{
    uint32_t first_kind = first[0];
    if (first_kind < 2u || second[0] < 2u) return 1;
    if (first_kind == 4u) {
        if (second[0] == 4u)
            return (int32_t)(second[1] - first[1]);
        return first[1] == 0u ? 1 : -1;
    }
    if (second[0] != 4u) {
        if (first_kind != 2u) {
            if (second[0] == 2u) return first[1] == 0u ? 1 : -1;
            const uint32_t sign = first[1];
            if (sign != second[1]) return sign == 0u ? 1 : -1;
            if ((int32_t)second[2] < (int32_t)first[2])
                return sign == 0u ? 1 : -1;
            if ((int32_t)first[2] < (int32_t)second[2])
                return sign != 0u ? 1 : -1;
            if (second[4] < first[4] ||
                (second[4] == first[4] && second[3] < first[3]))
                return sign == 0u ? 1 : -1;
            if (second[4] <= first[4]) {
                if (second[4] == first[4] && second[3] <= first[3])
                    return 0;
            }
            return sign == 0u ? -1 : 1;
        }
        if (second[0] == 2u) return 0;
    }
    return second[1] == 0u ? -1 : 1;
}
