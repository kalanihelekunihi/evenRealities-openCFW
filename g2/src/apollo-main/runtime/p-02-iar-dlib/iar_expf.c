/* IAR DLIB single-precision exp, firmware 2.2.6.10.
 * Native body is split: 0x43ba98..0x43baf2 (entry, |x| > ~229 and x == 0 paths)
 * and 0x43bfd0..0x43c08e (reduction, rational kernel, scaling). The constant
 * table is ROM 0x7088a0 (16 words). The only stock callers are inside the closed
 * nrf_fuel_gauge library (0x43a7ca, 0x43abf2); the function itself is libm.
 *
 * Algorithm: n = trunc(x*log2(e) +- 0.5), r = x - n*ln2_hi - n*ln2_lo, then
 * e^r = (1 + p + r*q) / (1 + p - r*q) with z = r*r, p = z*P1, q = 0.5 + z*P2.
 * The result is scaled by 2^n in one or two steps. ERANGE (34) is raised on
 * overflow to inf, on underflow to 0, and for finite x > ~229. It is not raised
 * for finite x < ~-229, which returns +0 directly.
 *
 * Stock uses chained (non-fused) VMLA/VMLS, so contraction is disabled.
 * Needs the hard-float S0 calling convention (profile g2-apollo-main-3 flags). */
#include <stdint.h>

#pragma STDC FP_CONTRACT OFF

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

extern void audio_uart_ring_errno_range_set_439cb2(void); /* errno = ERANGE (34) */

/* ROM 0x7088a0. */
static const uint32_t iar_expf_table[16] = {
    0x3f800000u, /* [0]  1.0                        */
    0x3f000000u, /* [1]  0.5 (rounding bias)        */
    0x3fb8aa3bu, /* [2]  log2(e)                    */
    0x7f800000u, /* [3]  +inf                       */
    0x3f316000u, /* [4]  ln2 high part 0.69287109375 */
    0x3990bfbfu, /* [5]  ln2 low part               */
    0x33000001u, /* [6]  |r| threshold ~2.98e-8      */
    0x3dccbf9eu, /* [7]  P1 0.0999748558            */
    0x3c085413u, /* [8]  P2 0.00832082611           */
    0x3f000000u, /* [9]  0.5                        */
    0x3f800000u, /* [10] 1.0                        */
    0x7f000000u, /* [11] 2^127                      */
    0x00800000u, /* [12] 2^-126                     */
    0x3e800000u, /* [13] 0.25 (unused here)          */
    0x3f317218u, /* [14] ln2 (unused here)           */
    0x86ca0002u, /* [15] |x| limit as (bits << 1), |x| ~= 229.000015 */
};

static float from_bits(uint32_t bits)
{
    union { uint32_t u; float f; } v = { .u = bits };
    return v.f;
}

static uint32_t to_bits(float value)
{
    union { float f; uint32_t u; } v = { .f = value };
    return v.u;
}

static float table_value(unsigned index)
{
    return from_bits(iar_expf_table[index]);
}

IAR_VFP float iar_expf_43ba98(float x)
{
    const uint32_t ix = to_bits(x);

    if ((ix << 1) > iar_expf_table[15]) {
        if ((ix << 1) >= 0xff000000u) {
            if ((ix << 1) > 0xff000000u)
                return x;                    /* NaN */
            return (ix & 0x80000000u) ? 0.0f /* -inf */ : x /* +inf */;
        }
        if ((ix & 0x80000000u) == 0u) {
            audio_uart_ring_errno_range_set_439cb2();
            return table_value(3);           /* +inf */
        }
        return table_value(1) - table_value(1); /* +0, errno untouched */
    }
    if (x == 0.0f)
        return table_value(0);

    float bias = table_value(1);
    if (ix & 0x80000000u)
        bias = -bias;
    const int32_t n = (int32_t)(bias + x * table_value(2));
    const float fn = (float)n;
    float r = x - fn * table_value(4);
    r = r - fn * table_value(5);

    float mantissa = table_value(0);
    const float abs_r = r < 0.0f ? -r : r;
    if (!(abs_r < table_value(6))) {
        const float z = r * r;
        const float p = z * table_value(7);
        const float q = table_value(9) + z * table_value(8);
        const float numerator = (p + r * q) + table_value(10);
        const float denominator = (p - r * q) + table_value(10);
        mantissa = mantissa * (numerator / denominator);
    }

    int32_t exponent = n + 127;
    float scale;
    if (exponent != 0 && (uint32_t)exponent < 255u) {
        scale = from_bits((uint32_t)exponent << 23);
    } else if (exponent >= 1) {
        /* 2^n above 2^127: take 2^127 out of the mantissa first. */
        exponent -= 127;
        if ((uint32_t)exponent < 255u) {
            scale = from_bits((uint32_t)exponent << 23);
            mantissa = mantissa * table_value(11);
        } else {
            scale = table_value(3);
        }
    } else {
        /* 2^n below 2^-126: take 2^-126 out of the mantissa first. */
        exponent += 126;
        if (exponent >= 1) {
            scale = from_bits((uint32_t)exponent << 23);
            mantissa = mantissa * table_value(12);
        } else {
            scale = mantissa - mantissa;
        }
    }

    const float result = scale * mantissa;
    if (result == 0.0f || (to_bits(result) << 1) == 0xff000000u)
        audio_uart_ring_errno_range_set_439cb2();
    return result;
}
