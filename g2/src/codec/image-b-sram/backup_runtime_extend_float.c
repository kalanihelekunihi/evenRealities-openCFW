/* SPDX-License-Identifier: MIT
 * IEEE-754 binary32 to binary64 widening required by native IMCRA %f
 * logging. Finite inputs are exact and require no floating arithmetic.
 * Signaling-NaN quieting/exception flags remain a target ABI gate.
 */
#include <stdint.h>

double __extendsfdf2(float input)
{
    union { float value; uint32_t bits; } source;
    union { double value; uint64_t bits; } result;
    source.value = input;
    uint32_t sign = source.bits >> 31;
    uint32_t exponent = (source.bits >> 23) & 0xffu;
    uint32_t fraction = source.bits & UINT32_C(0x7fffff);
    uint64_t fraction64;
    uint32_t exponent64;
    if (exponent == 0xffu) {
        exponent64 = 0x7ffu;
        fraction64 = (uint64_t)fraction << 29;
    } else if (exponent == 0u) {
        if (fraction == 0u) {
            exponent64 = 0u;
            fraction64 = 0u;
        } else {
            uint32_t leading = 31u - (uint32_t)__builtin_clz(fraction);
            exponent64 = leading + 874u;
            fraction64 = ((uint64_t)fraction << (52u - leading)) &
                         UINT64_C(0x000fffffffffffff);
        }
    } else {
        exponent64 = exponent + 896u;
        fraction64 = (uint64_t)fraction << 29;
    }
    result.bits = ((uint64_t)sign << 63) |
                  ((uint64_t)exponent64 << 52) | fraction64;
    return result.value;
}
