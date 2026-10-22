/* IAR DLIB fminf / fmaxf (VFP entries, x in s0, y in s1). No source path is
 * retained. Native rows 0x439efc..0x439f24 and 0x439f88..0x439fb4.
 * Callers include nrf_fuel_gauge (0x439d72, 0x439d88) and 0x599714/0x59bae4.
 *
 * Single-precision FP: build with profile g2-apollo-main-3. Stock passes x, y
 * and the result in s0/s1 (IAR VFP ABI), so both entries are pcs("aapcs-vfp"). */
#include <stdint.h>

typedef union { float f; uint32_t u; } p01_minmax_bits_t;

static uint32_t p01_float_bits(float value)
{
    p01_minmax_bits_t v = { .f = value };
    return v.u;
}

/* A NaN y returns x; a NaN x returns y. With x == +0.0 and y == +-0.0 the
 * result is y, so fminf(+0, -0) is -0 (fminf(-0, +0) keeps -0 via the
 * ordinary compare). */
__attribute__((pcs("aapcs-vfp"))) float fminf_439efc(float x, float y)
{
    if (y != y)
        return x;
    if (p01_float_bits(x) == 0u && y == 0.0f)
        return y;
    if (x != x || y < x)
        return y;
    return x;
}

/* A NaN y returns x; a NaN x returns y. With y == +-0.0 and x == +-0.0 the
 * result is y when x is -0 and x when x is +0, so fmaxf(-0, +0) is +0. */
__attribute__((pcs("aapcs-vfp"))) float fmaxf_439f88(float x, float y)
{
    if (y != y)
        return x;
    if (y == 0.0f && (p01_float_bits(x) << 1) == 0u)
        return (p01_float_bits(x) & 0x80000000u) ? y : x;
    if (x != x || x < y)
        return y;
    return x;
}
