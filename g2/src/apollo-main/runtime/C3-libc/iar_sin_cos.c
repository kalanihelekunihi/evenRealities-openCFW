/* IAR DLIB double-precision _Sin kernel and cos, firmware 2.2.6.10.
 *
 *   _Sin(x, qoff)  native 0x508b68..0x508da7, literal pool 0x508da8..0x508e57
 *                  (22 doubles; no ROM table outside the pool)
 *   cos(x)         native 0x508e58..0x508e5b: movs r0,#1; b 0x508b68
 *
 * No sin entry (movs r0,#0; b 0x508b68) exists in the image: the only branch
 * to 0x508b68 is the cos thunk, and the only stock caller of cos is the IMU
 * tilt-threshold path (bl at 0x4a3d88, imu_icm45608_fp.c).
 *
 * Algorithm (stock order kept, no fused multiply-add):
 *   g = x * 2/pi.
 *   |g| < 2147483646.5: q = (int)(g + copysign(0.5, g)) (VCVT truncates);
 *       if q != 0, x += (q * 2^-28) * c[i] for the five Cody-Waite pieces of
 *       -pi/2 * 2^28 (each product is exact).
 *   otherwise: Inf -> 0x7fffffffffffffff, NaN -> x, +-0 -> qoff ? 1.0 : x
 *       (dead: zero takes the first branch), else g + copysign(0.5, g) is
 *       truncated to an integer in place by clearing fraction bits, used for
 *       the same reduction (scaled by the 2^-28 literal), and converted with
 *       saturating VCVT.S32.F64 for the quadrant.
 *   n = (q & 3) + qoff; |x| < 2^-27 returns x (or 1.0 if n is odd); odd n
 *   evaluates the cosine polynomial 1 + w*C(w), even n x + x*w*S(w), w = x*x;
 *   bit 1 of n negates the result.
 * The function never touches errno (no store, no call): Inf returns the
 * all-ones-mantissa NaN silently, unlike asin/sqrt in this tree.
 *
 * Stock passes x in D0, qoff in R0 and returns D0 (IAR hard-float), so every
 * entry is pcs("aapcs-vfp"); needs a double-precision FPU (profile
 * g2-apollo-main-20: -mfpu=fpv5-d16). */
#include <stdint.h>

#pragma STDC FP_CONTRACT OFF

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

/* Must match the extern in drivers/peripherals/imu-icm45608/imu_icm45608_fp.c
 * (G2_IMU_VFP == pcs("aapcs-vfp")). */
IAR_VFP double iar_cos_508e58(double x);
/* Exported (no other caller) so the qoff argument stays a real R0 parameter
 * instead of being constant-propagated from the cos thunk. */
IAR_VFP double iar_sin_508b68(double x, uint32_t qoff);

#define SIN_SIGN_BIT 0x8000000000000000ull
#define SIN_HALF_HI 0x3fe00000u               /* vmov.f64 #0.5, high word */
#define SIN_ONE_BITS 0x3ff0000000000000ull    /* vmov.f64 #1.0 */

#define SIN_TWO_OVER_PI 0x3fe45f306dc9c883ull /* 0x508da8, 2/pi */
#define SIN_HUGE_RAD 0x41dfffffffa00000ull    /* 0x508db0, 2147483646.5 */
#define SIN_INF_RESULT 0x7fffffffffffffffull  /* 0x508de0, NaN for +-Inf */
#define SIN_TWO_M28 0x3e30000000000000ull     /* 0x508de8, 2^-28 */
#define SIN_EPS 0x3e40000000000000ull         /* 0x508df0, 2^-27 */

/* 0x508db8..0x508dd8: -pi/2 * 2^28 split into five short pieces. */
static const uint64_t sin_pio2_pieces[5] = {
    0xc1b921fb50000000ull, /* 0x508db8 */
    0xc01110b460000000ull, /* 0x508dc0 */
    0xbe51a62620000000ull, /* 0x508dc8 */
    0xbcd3145c00000000ull, /* 0x508dd0 */
    0xbb3b839a20000000ull, /* 0x508dd8 */
};

/* 0x508df8..0x508e20: cosine coefficients, highest order first. */
static const uint64_t sin_cos_coef[6] = {
    0x3e21ba39100a2609ull, /* 0x508df8  C0 ~  2.0637e-09 */
    0xbe927df9c661a83bull, /* 0x508e00  C1 ~ -2.7555e-07 */
    0x3efa019f9030ac63ull, /* 0x508e08  C2 ~  2.4802e-05 */
    0xbf56c16c1651fbf6ull, /* 0x508e10  C3 ~ -1/720 */
    0x3fa55555555502b1ull, /* 0x508e18  C4 ~  1/24 */
    0xbfdfffffffffffaeull, /* 0x508e20  C5 ~ -1/2 */
};

/* 0x508e28..0x508e50: sine coefficients, highest order first. */
static const uint64_t sin_sin_coef[6] = {
    0x3de5d810c32f8fb0ull, /* 0x508e28  S0 ~  1.5894e-10 */
    0xbe5ae5e1a1730c8full, /* 0x508e30  S1 ~ -2.5051e-08 */
    0x3ec71de34fe4ad4dull, /* 0x508e38  S2 ~  2.7557e-06 */
    0xbf2a01a019b5e33eull, /* 0x508e40  S3 ~ -1/5040 */
    0x3f8111111110f0faull, /* 0x508e48  S4 ~  1/120 */
    0xbfc5555555555542ull, /* 0x508e50  S5 ~ -1/6 */
};

static double from_bits(uint64_t bits)
{
    union { uint64_t u; double d; } v = { .u = bits };
    return v.d;
}

static uint64_t to_bits(double value)
{
    union { double d; uint64_t u; } v = { .d = value };
    return v.u;
}

/* copysign(0.5, g) built from the high word of g, as stock does. */
static double half_with_sign_of(double g)
{
    uint64_t sign = to_bits(g) & SIN_SIGN_BIT;
    return from_bits(sign | ((uint64_t)SIN_HALF_HI << 32));
}

/* Inline _Dint at 0x508c6a: clear the fraction bits of a double. */
static double truncate_bits(double value)
{
    uint64_t bits = to_bits(value);
    if ((bits << 1) != 0) {
        int32_t shift = 1075 - (int32_t)((bits << 1) >> 53);
        if (shift >= 53) {
            bits &= SIN_SIGN_BIT;
        } else if (shift > 0) {
            bits &= ~0ull << shift;
        }
    }
    return from_bits(bits);
}

/* VCVT.S32.F64 (round toward zero, saturating). The argument is integral. */
static int32_t vcvt_s32(double value)
{
    if (value >= 2147483648.0) {
        return INT32_MAX;
    }
    if (value < -2147483648.0) {
        return INT32_MIN;
    }
    return (int32_t)value;
}

/* x + g*(-pi/2 * 2^28) in five pieces; g is already scaled by 2^-28. */
static double reduce(double x, double g)
{
    x = x + g * from_bits(sin_pio2_pieces[0]);
    x = x + g * from_bits(sin_pio2_pieces[1]);
    x = x + g * from_bits(sin_pio2_pieces[2]);
    x = x + g * from_bits(sin_pio2_pieces[3]);
    x = x + g * from_bits(sin_pio2_pieces[4]);
    return x;
}

/* _Sin at 0x508b68: qoff = 0 gives sin, 1 gives cos. */
IAR_VFP double iar_sin_508b68(double x, uint32_t qoff)
{
    double g = x * from_bits(SIN_TWO_OVER_PI);
    uint32_t quad;

    if (from_bits(to_bits(g) & ~SIN_SIGN_BIT) < from_bits(SIN_HUGE_RAD)) {
        g = half_with_sign_of(g) + g;
        quad = (uint32_t)(int32_t)g;
        if (quad != 0) {
            x = reduce(x, (double)(int32_t)quad * from_bits(SIN_TWO_M28));
        }
    } else {
        uint64_t bits = to_bits(x);

        if (((bits << 1) >> 53) == 0x7ffu) { /* exponent all ones */
            if ((bits << 12) != 0) {
                return x; /* NaN */
            }
            return from_bits(SIN_INF_RESULT);
        }
        if ((bits & ~SIN_SIGN_BIT) == 0) {
            if (qoff == 0) {
                return x;
            }
            return from_bits(SIN_ONE_BITS);
        }
        g = half_with_sign_of(g) + g;
        g = truncate_bits(g);
        if ((to_bits(g) & ~SIN_SIGN_BIT) != 0) {
            x = reduce(x, g * from_bits(SIN_TWO_M28));
        }
        quad = (uint32_t)vcvt_s32(g);
    }

    qoff = (quad & 3u) + qoff;
    if (from_bits(to_bits(x) & ~SIN_SIGN_BIT) < from_bits(SIN_EPS)) {
        if (qoff & 1u) {
            x = from_bits(SIN_ONE_BITS);
        }
    } else {
        double w = x * x;
        double p;

        if (qoff & 1u) {
            p = from_bits(sin_cos_coef[1]) + w * from_bits(sin_cos_coef[0]);
            p = from_bits(sin_cos_coef[2]) + p * w;
            p = from_bits(sin_cos_coef[3]) + p * w;
            p = from_bits(sin_cos_coef[4]) + p * w;
            p = from_bits(sin_cos_coef[5]) + p * w;
            x = from_bits(SIN_ONE_BITS) + p * w;
        } else {
            double xw;
            p = from_bits(sin_sin_coef[1]) + w * from_bits(sin_sin_coef[0]);
            p = from_bits(sin_sin_coef[2]) + p * w;
            p = from_bits(sin_sin_coef[3]) + p * w;
            p = from_bits(sin_sin_coef[4]) + p * w;
            xw = x * w;
            p = from_bits(sin_sin_coef[5]) + p * w;
            x = x + xw * p;
        }
    }
    if (qoff & 2u) {
        x = -x;
    }
    return x;
}

/* cos at 0x508e58. */
IAR_VFP double iar_cos_508e58(double x)
{
    return iar_sin_508b68(x, 1u);
}
