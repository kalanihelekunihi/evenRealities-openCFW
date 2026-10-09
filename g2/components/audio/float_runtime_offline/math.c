#include "math.h"
#include <stdint.h>
static uint32_t bits(float x) {
    union { float f; uint32_t u; } value = { .f = x };
    return value.u;
}
static float value(uint32_t x) {
    union { float f; uint32_t u; } result = { .u = x };
    return result.f;
}
float audio_floorf(float input) {
    uint32_t x = bits(input);
    int32_t exponent = (int32_t)((x >> 23) & 255) - 126;
    if (exponent <= 0) {
        if ((x << 1) == 0) return input;
        return value((x >> 31) ? 0xbf800000 : 0);
    }
    if (exponent >= 24) return input;
    uint32_t mask = 0x00ffffffu >> exponent;
    if (x >> 31) x += mask;
    return value(x & ~mask);
}
float audio_roundf(float input) {
    uint32_t x = bits(input);
    int32_t exponent = (int32_t)((x >> 23) & 255) - 126;
    if (exponent <= 0)
        return value((x & 0x80000000u) | (exponent == 0 ? 0x3f800000u : 0));
    if (exponent >= 24) return input;
    uint32_t mask = 0x00ffffffu >> exponent;
    x &= ~(mask >> 1);
    x += mask;
    return value(x & ~mask);
}
float audio_ceilf(float input) {
    uint32_t x = bits(input);
    int32_t exponent = (int32_t)((x >> 23) & 255) - 126;
    if (exponent <= 0) {
        if ((x << 1) == 0) return input;
        return value((x >> 31) ? 0x80000000u : 0x3f800000u);
    }
    if (exponent >= 24) return input;
    uint32_t mask = 0x00ffffffu >> exponent;
    if (!(x >> 31)) x += mask;
    return value(x & ~mask);
}
/* ARM register LSR returns zero for a shift >=32, unlike unchecked C shifts. */
static uint32_t right_shift(uint32_t x, uint32_t count) {
    return count >= 32 ? 0 : x >> count;
}
float audio_fmodf(float numerator, float denominator) {
    uint32_t x = bits(numerator), y = bits(denominator);
    uint32_t sign = x & 0x80000000u, y_double = y << 1;
    int32_t ex = (x >> 23) & 255, ey = y_double >> 24;
    uint32_t x_norm, y_norm;
    if (!y_double || ex == 255 || ey == 0 || ey == 255) {
        if (!y_double || ex == 255 || ey == 255) {
            /* Exact stock CMN/carry path: finite / zero sets errno33.
             * Infinite/NaN numerator or NaN denominator does not set errno. */
            if (ex != 255 && ey == 255 && y_double == 0xff000000u)
                return numerator;
            if (ex != 255 && ey != 255)
                *(volatile uint32_t *)0x20074f14 = 33;
            return value(0x7fffffffu);
        }
        if (y_double >= (x << 1))
            return y_double == (x << 1) ? value(sign) : numerator;
        y_norm = y_double << 8;
        uint32_t leading = __builtin_clz(y_norm);
        y_norm <<= leading;
        ey = -(int32_t)leading;
        if (ex == 0) {
            x_norm = x << 9;
            leading = __builtin_clz(x_norm);
            x_norm <<= leading;
            ex = -(int32_t)leading;
        } else {
            x_norm = 0x80000000u | (x << 8);
        }
    } else {
        if (y_double >= (x << 1))
            return y_double == (x << 1) ? value(sign) : numerator;
        y_norm = 0x80000000u | (y_double << 7);
        x_norm = 0x80000000u | (x << 8);
    }
    uint32_t divisor = y_norm >> 8;
    int32_t remaining = ex - ey;
    while (remaining > 8) {
        x_norm = (x_norm % divisor) << 8;
        if (!x_norm) return value(sign);
        remaining -= 8;
    }
    x_norm = right_shift(x_norm, (uint32_t)(8 - remaining));
    x_norm %= divisor;
    if (!x_norm) return value(sign);
    uint32_t leading = __builtin_clz(x_norm);
    x_norm <<= leading;
    int32_t result_exponent = ey + 7 - (int32_t)leading;
    if (result_exponent < 0)
        return value(sign | right_shift(x_norm, (uint32_t)(8 - result_exponent)));
    return value((sign | (x_norm >> 8)) + ((uint32_t)result_exponent << 23));
}
