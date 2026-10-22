/* IAR DLIB (EWARM 9.x) floating-point conversion leaves, firmware 2.2.6.10.
 * IAR DLIB has no public source; freestanding equivalents written from the
 * disassembly. Needs the double-precision FPU: profile g2-apollo-main-20.
 *   0x541bbc..0x541bc9  softfp _Stodx wrapper (shared epilogue 0x541bbc..0x541bc1
 *                       placed before the entry 0x541bc2): d0 result -> r0:r1
 *   0x541bca..0x541bd7  softfp double -> float (vcvt.f32.f64), x in r0:r1
 *   0x542a80..0x542c19  _Dtento: x * 10^n with range check (VFP: x d0, n r0, perr r1)
 *   0x542d44..0x542d47  _Stod  = _Stodx(s, endptr, pten, NULL)
 *   0x542d48..0x542d4b  strtod = _Stod(s, endptr, 0)
 * _Stodx itself is stodx_542c20 in runtime/iar-dlib-gaps/iar_strtod.c. */
#include <stdint.h>
#include <stddef.h>

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))
#define IAR_SOFT __attribute__((pcs("aapcs")))

extern IAR_VFP double stodx_542c20(const char *s, char **endptr, int32_t pten, int32_t *perr);
extern IAR_VFP double frexp_4d4138(double value, int32_t *exponent);
extern IAR_VFP double dscale_4d4208(double value, int32_t n); /* value * 2^n */
extern void audio_uart_ring_errno_range_set_439cb2(void);      /* errno = ERANGE */

#define DTENTO_TABLE_STEPS 8u

/* 10^(2^i); the loops use the first eight, larger exponents repeat 1e+-256. */
static const double pows[9] = {1e1, 1e2, 1e4, 1e8, 1e16, 1e32, 1e64, 1e128, 1e256}; /* ROM 0x6ff7d8 */
static const double tiny_step = 1e-256; /* ROM 0x542d0c */
static const double huge_step = 1e256;  /* ROM 0x542d14 */

IAR_SOFT double strtod_541bc2(const char *s, char **endptr, int32_t pten, int32_t *perr);
IAR_SOFT float double_to_float_541bca(double x);
IAR_VFP double dtento_542a80(double x, int32_t n, int32_t *perr);
IAR_VFP double stod_542d44(const char *s, char **endptr, int32_t pten);
IAR_VFP double strtod_542d48(const char *s, char **endptr);

static uint64_t double_bits(double value)
{
    union { double d; uint64_t u; } v = { .d = value };
    return v.u;
}

/* Stock classifies with the high word only: zero is all bits but the sign
 * clear, infinity is exponent 0x7ff with the top 20 mantissa bits clear. */
static int is_zero(double x)
{
    return (double_bits(x) & 0x7fffffffffffffffu) == 0u;
}

static int is_inf_hi(double x)
{
    uint32_t hi = (uint32_t)(double_bits(x) >> 32);
    return ((hi >> 20) & 0x7ffu) == 0x7ffu && (hi & 0xfffffu) == 0u;
}

/* Stock 0x541BBC (FUN_00541bc2: epilogue of strtod_541bc2 placed before its entry) */
IAR_SOFT double strtod_541bc2(const char *s, char **endptr, int32_t pten, int32_t *perr)
{
    return stodx_542c20(s, endptr, pten, perr);
}

IAR_SOFT float double_to_float_541bca(double x)
{
    return (float)x;
}

/* Builds 10^|n| from the table (at most eight steps), applies it to the
 * frexp mantissa and rescales; any remaining exponent is applied one 1e+-256
 * step at a time. A zero or infinite result raises ERANGE and *perr |= 1. */
IAR_VFP double dtento_542a80(double x, int32_t n, int32_t *perr)
{
    double factor = 1.0;
    const double *p = pows;
    uint32_t steps = DTENTO_TABLE_STEPS;
    int32_t e;

    if (n == 0 || is_zero(x) || is_inf_hi(x))
        return x;
    if (n < 0) {
        uint32_t nu = 0u - (uint32_t)n;

        while (nu != 0u && steps != 0u) {
            if ((nu & 1u) != 0u)
                factor *= *p;
            nu >>= 1;
            p++;
            steps--;
        }
        x = frexp_4d4138(x, &e);
        x = dscale_4d4208(x / factor, e);
        if (!is_zero(x) && !is_inf_hi(x) && nu != 0u) {
            do {
                x = frexp_4d4138(x, &e);
                x = dscale_4d4208(x * tiny_step, e);
                if (is_zero(x) || is_inf_hi(x))
                    break;
            } while (--nu != 0u);
        }
    } else {
        do {
            if ((n & 1) != 0)
                factor *= *p;
            n >>= 1;
            p++;
            steps--;
        } while (n > 0 && steps != 0u);
        x = frexp_4d4138(x, &e);
        x = dscale_4d4208(x * factor, e);
        if (!is_zero(x) && !is_inf_hi(x) && n > 0) {
            do {
                x = frexp_4d4138(x, &e);
                x = dscale_4d4208(x * huge_step, e);
                if (is_zero(x) || is_inf_hi(x))
                    break;
            } while (--n > 0);
        }
    }
    if (is_zero(x) || is_inf_hi(x)) {
        audio_uart_ring_errno_range_set_439cb2();
        if (perr != NULL)
            *perr |= 1;
    }
    return x;
}

IAR_VFP double stod_542d44(const char *s, char **endptr, int32_t pten)
{
    return stodx_542c20(s, endptr, pten, NULL);
}

IAR_VFP double strtod_542d48(const char *s, char **endptr)
{
    return stod_542d44(s, endptr, 0);
}
