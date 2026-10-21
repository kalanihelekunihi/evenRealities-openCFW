/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x1020a574..0x1020a702. Five-word soft-float
 * parts to IEEE-754 double, with stock round-to-nearest-even and
 * quiet-NaN output. Native execution and final target ABI equivalence
 * remain unqualified.
 */
#include <stdint.h>

uint64_t gx8002_xip_pack_double_1020a574(const uint32_t parts[5])
{
    const uint64_t sign = ((uint64_t)(parts[1] & 1u)) << 63u;
    const uint32_t kind = parts[0];
    const uint64_t mantissa = ((uint64_t)parts[4] << 32u) | parts[3];
    if (kind < 2u) {
        const uint64_t payload =
            (mantissa >> 8u) & ((UINT64_C(1) << 52u) - 1u);
        return sign | (UINT64_C(0x7ff) << 52u) |
            payload | (UINT64_C(1) << 51u);
    }
    if (kind == 4u) return sign | (UINT64_C(0x7ff) << 52u);
    if (kind == 2u || mantissa == 0u) return sign;

    const int32_t exponent = (int32_t)parts[2];
    if (exponent > 1023) return sign | (UINT64_C(0x7ff) << 52u);
    if (exponent >= -1022) {
        uint64_t rounded =
            (mantissa + UINT64_C(0x7f) + ((mantissa >> 8u) & 1u)) >> 8u;
        uint32_t biased = (uint32_t)(exponent + 1023);
        if (rounded >= (UINT64_C(1) << 53u)) {
            rounded >>= 1u;
            ++biased;
        }
        if (biased >= 2047u) return sign | (UINT64_C(0x7ff) << 52u);
        return sign | ((uint64_t)biased << 52u) |
            (rounded & ((UINT64_C(1) << 52u) - 1u));
    }

    const uint32_t shift = (uint32_t)(-1022 - exponent) + 8u;
    if (shift >= 64u) return sign;
    uint64_t rounded = mantissa >> shift;
    const uint64_t lost = mantissa & ((UINT64_C(1) << shift) - 1u);
    const uint64_t half = UINT64_C(1) << (shift - 1u);
    if (lost > half || (lost == half && (rounded & 1u) != 0u)) ++rounded;
    if (rounded >= (UINT64_C(1) << 52u))
        return sign | (UINT64_C(1) << 52u);
    return sign | rounded;
}
