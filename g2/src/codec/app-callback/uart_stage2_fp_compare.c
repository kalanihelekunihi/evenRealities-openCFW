/* SPDX-License-Identifier: MIT
 * Retained stage2 soft-FP internal comparator at 0x10007e10.
 * Class 0/1 is unordered, class 2 is zero, class 4 is infinity, and class 3
 * carries exponent and two significand limbs. Return orientation follows the
 * stock helper and is intentionally not C's ordinary memcmp ordering.
 */
#include <stdint.h>

int32_t gx8002_uart_stage2_fp_compare_7e10(
    const uint32_t left[5], const uint32_t right[5])
{
    uint32_t lc = left[0];
    if (lc < 2u || right[0] < 2u) return 1;
    if (lc == 4u) {
        if (right[0] == 4u) return (int32_t)(right[1] - left[1]);
        return left[1] == 0u ? 1 : -1;
    }
    if (right[0] != 4u) {
        if (lc != 2u) {
            if (right[0] == 2u) return left[1] == 0u ? 1 : -1;
            uint32_t sign = left[1];
            if (sign != right[1] ||
                (int32_t)right[2] < (int32_t)left[2])
                return sign == 0u ? 1 : -1;
            if ((int32_t)left[2] < (int32_t)right[2])
                return sign != 0u ? 1 : -1;
            if (right[4] < left[4] ||
                (right[4] == left[4] && right[3] < left[3]))
                return sign == 0u ? 1 : -1;
            if (right[4] <= left[4]) {
                if (right[4] != left[4]) return 0;
                if (right[3] <= left[3]) return 0;
            }
            return sign == 0u ? -1 : 1;
        }
        if (right[0] == 2u) return 0;
    }
    return right[1] == 0u ? -1 : 1;
}
