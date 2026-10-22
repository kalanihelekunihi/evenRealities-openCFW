/* IAR DLIB double-precision asin, native 0x43c260..0x43c36e, firmware 2.2.6.10.
 * Literals: 0x43c2d8 (sqrt(0.5)), 0x43c2e0 (1.0). Shared arctangent table:
 * 0x43c370..0x43c400 (18 doubles). The only stock caller is the audio
 * service_algo_delay_to_angle (0x5918c6).
 *
 * asin(x) = atan(|x| / sqrt((1+|x|)(1-|x|))) for |x| <= sqrt(0.5), and
 * pi/2 - atan(sqrt(...) / |x|) above it. The atan kernel (entry 0x43c2e8) reduces
 * t >= 2-sqrt(3) with t' = (sqrt(3)t - 1)/(sqrt(3) + t) (+pi/6). It evaluates
 * t + t*z*P(z) / Q(z) with z = t*t unless |t| < 2^-27, then adds an offset from
 * {0, pi/6, pi/2, pi/3} and restores the sign. |x| > 1 sets EDOM (33) and returns
 * |x| with its high word forced to 0x7fffffff. A NaN whose |high word| exceeds
 * 0x7ff00000 is returned as |x| without errno.
 *
 * Stock uses chained (non-fused) VMLA, so contraction is disabled.
 * Needs the hard-float D0 calling convention and a double-precision FPU
 * (profile g2-apollo-main-20: -mfpu=fpv5-d16). */
#include <stdint.h>

#pragma STDC FP_CONTRACT OFF

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

extern void audio_uart_float_domain_error_439ca4(void); /* errno = EDOM (33) */

#define ASIN_SPLIT_BITS 0x3fe6a09e667f3bceull /* ROM 0x43c2d8, sqrt(0.5) */
#define ASIN_ONE_BITS 0x3ff0000000000000ull   /* ROM 0x43c2e0, 1.0 */

/* ROM 0x43c370. Entries 14..17 are not reached from asin. */
static const uint64_t iar_atan_table[18] = {
    0x3fd126145e9ecd57ull, /* [0]  2 - sqrt(3), reduction threshold */
    0x3ff0000000000000ull, /* [1]  1.0 */
    0x3ffbb67ae8584caaull, /* [2]  sqrt(3) */
    0x3fb0574b13575d84ull, /* [3]  P2 */
    0x3fe45eed194c93b2ull, /* [4]  P1 */
    0x3ff84002b902debeull, /* [5]  P0 */
    0x3f74c0c78f0239deull, /* [6]  Q3 */
    0x3fc80c008312ab8aull, /* [7]  Q2 */
    0x3ff0d8b608e5d724ull, /* [8]  Q1 */
    0x3ffd95580e58340full, /* [9]  Q0 */
    0x0000000000000000ull, /* [10] 0 */
    0x3fe0c152382d7366ull, /* [11] pi/6 */
    0x3ff921fb54442d18ull, /* [12] pi/2 */
    0x3ff0c152382d7366ull, /* [13] pi/3 */
    0x3ff921fb54442d18ull, /* [14] pi/2 */
    0x4000c152382d7366ull, /* [15] 2pi/3 */
    0x400921fb54442d18ull, /* [16] pi */
    0x4004f1a6c638d03full, /* [17] 5pi/6 */
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

static double table_value(unsigned index)
{
    return from_bits(iar_atan_table[index]);
}

/* Stock uses VSQRT.F64 directly (no errno path); __builtin_sqrt would call sqrt. */
static double vfp_sqrt(double value)
{
    double result;
    __asm__("vsqrt.f64 %P0, %P1" : "=w"(result) : "w"(value));
    return result;
}

/* Arctangent kernel at 0x43c2e8. flags bit0 = negate result, bit2 = return
 * pi/2 - atan(t); bit1 is set here when the argument is range-reduced. */
static double atan_kernel(double t, uint32_t flags)
{
    if (!(t < table_value(0))) {
        t = (-table_value(1) + t * table_value(2)) / (table_value(2) + t);
        flags |= 2u;
    }
    if (((uint32_t)(to_bits(t) >> 32) & 0x7fffffffu) >= 0x3e400000u) {
        const double z = t * t;
        double p = table_value(4) + table_value(3) * z;
        const double tz = t * z;
        p = table_value(5) + p * z;
        t = t + p * tz;
        double q = table_value(7) + table_value(6) * z;
        q = table_value(8) + q * z;
        q = table_value(9) + q * z;
        q = table_value(1) + q * z;
        t = t / q;
    }
    const uint32_t negative = flags & 1u;
    const uint32_t offset = flags >> 1;
    if (offset & 2u)
        t = -t;
    t = t + table_value(10u + offset);
    if (negative)
        t = -t;
    return t;
}

IAR_VFP double iar_asin_43c260(double x)
{
    const uint64_t bits = to_bits(x);
    const uint32_t low = (uint32_t)bits;
    const uint32_t high = (uint32_t)(bits >> 32);
    const uint32_t magnitude_high = high & 0x7fffffffu;
    uint32_t flags = high >> 31;
    const double a = from_bits(bits & 0x7fffffffffffffffull);

    if (magnitude_high == 0u && low == 0u)
        return x; /* +-0 */
    if (magnitude_high > 0x3ff00000u || (magnitude_high == 0x3ff00000u && low != 0u)) {
        if (magnitude_high > 0x7ff00000u)
            return a;
        audio_uart_float_domain_error_439ca4();
        return from_bits(((uint64_t)0x7fffffffu << 32) | low);
    }

    const double one = from_bits(ASIN_ONE_BITS);
    const double root = vfp_sqrt((one + a) * (one - a));
    double t;
    if (from_bits(ASIN_SPLIT_BITS) < a) {
        flags ^= 4u;
        t = root / a;
    } else {
        t = a / root;
    }
    return atan_kernel(t, flags);
}
