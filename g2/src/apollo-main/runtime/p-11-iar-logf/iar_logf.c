/* IAR DLIB single-precision natural logarithm, native 0x598074..0x59812d
 * (firmware 2.2.6.10). The constant table is ROM 0x70885c (9 floats, loaded
 * with one VLDMIA); the pool word is 0x598130. The only stock callers are
 * inside the closed nrf_fuel_gauge library (0x58eba4, 0x58ec02, 0x58ec64);
 * the function itself is libm.
 *
 * Algorithm: x = m * 2^e with m in [sqrt(0.5), sqrt(2)); f = m - 1,
 * s = f / (m + 1), z = s*s, R = z*(c6 + z*(c5 + z*c4)) and
 * log(x) = (f - ((f - R)*s - e*ln2_lo)) + e*ln2_hi.
 * Subnormals are scaled by 2^23 first. log(+-0) = -inf (no errno),
 * log(x<0) and log(-inf) give the NaN 0x7fffffff with EDOM (33) through the
 * veneer 0x577c34 -> 0x439ca4; NaN and +inf are returned unchanged.
 *
 * Stock uses chained (non-fused) VMLA/VMLS, so contraction is disabled.
 * Needs the hard-float S0 calling convention (profile g2-apollo-main-3 flags). */
#include <stdint.h>

#pragma STDC FP_CONTRACT OFF

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

extern void audio_uart_float_domain_error_439ca4(void); /* errno = EDOM (33) */

/* ROM 0x70885c. */
static const uint32_t iar_logf_table[9] = {
    0x3f3504f3u, /* [0] sqrt(0.5)                 */
    0x3f800000u, /* [1] 1.0                       */
    0x40000000u, /* [2] 2.0                       */
    0x4b000000u, /* [3] 2^23 (subnormal scaling)  */
    0x3e990215u, /* [4] c4 0.298844               */
    0x3eccae11u, /* [5] c5 0.399766               */
    0x3f2aaac0u, /* [6] c6 0.666668               */
    0x3f317216u, /* [7] ln2 high part             */
    0x33fbe8e8u, /* [8] ln2 low part              */
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
    return from_bits(iar_logf_table[index]);
}

static float domain_error(void)
{
    const float nan_value = from_bits(0x7fffffffu);
    audio_uart_float_domain_error_439ca4();
    return nan_value;
}

IAR_VFP float iar_logf_598074(float x)
{
    uint32_t ix = to_bits(x);

    if ((ix << 1) >= 0xff000000u) {
        if ((ix << 1) > 0xff000000u)
            return x;                  /* NaN */
        if (ix & 0x80000000u)
            return domain_error();     /* -inf */
        return x;                      /* +inf */
    }
    if (!(x > 0.0f)) {
        if (x < 0.0f)
            return domain_error();
        return from_bits(0xff800000u); /* -inf for +-0 */
    }

    int32_t e;
    if ((ix >> 23) == 0u) {
        x = x * table_value(3);
        ix = to_bits(x);
        e = (int32_t)(ix >> 23) - 126;
        ix -= (uint32_t)e << 23;
        e -= 23;
    } else {
        e = (int32_t)(ix >> 23) - 126;
        ix -= (uint32_t)e << 23;
    }

    float m = from_bits(ix);           /* in [0.5, 1) */
    if (m < table_value(0)) {
        e -= 1;
        m = m * table_value(2);
    }
    const float fe = (float)e;
    const float f = m - table_value(1);
    const float s = f / (m + table_value(1));
    const float z = s * s;
    const float q1 = table_value(5) + table_value(4) * z;
    const float q2 = table_value(6) + q1 * z;
    const float t = f - q2 * z;
    const float u = t * s - table_value(8) * fe;
    return (f - u) + table_value(7) * fe;
}
