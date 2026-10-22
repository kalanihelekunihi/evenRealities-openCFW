/* IAR DLIB strtof (Dinkumware-derived strtof -> _Stof -> _FDtento), reconstructed
 * from the 2.2.6.10 disassembly. IAR DLIB has no public source; this is a clean
 * freestanding equivalent.
 *
 * Stock ranges:
 *   0x00595708..0x0059585b  _FDtento  (x * 10^n with ERANGE/perr on 0 or Inf)
 *   0x0059585c..0x00595947  _Stof     (literal pool 0x595948..0x595963)
 *   0x00595964..0x00595969  strtof    (tail branch to _Stof with pten 0, perr NULL)
 *   ROM 0x59596c..0x595983  powers table {1e1, 1e2, 1e4, 1e8, 1e16, 1e32}
 * _FDtento and _Stof have no other callers; they are private to strtof.
 *
 * Shared scanners are the double strtod's: _Stopfx 0x585134, _Stoflt 0x585258,
 * _Stoxflt 0x585410. strtof asks for one significand chunk (maxsig 1): decimal
 * chunks are base 1e9, hex chunks base 2^28. _FDtento multiplies by at most
 * five table powers at once, then steps by 1e32/1e-32, each scaling done as
 * frexpf -> multiply/divide -> ldexpf. Stock 1e-32 is 0x0a4fb11e (one ulp below
 * the nearest binary32). Floats travel in s-registers (VFP ABI): profile
 * g2-apollo-main-3. */
#include <stdint.h>
#include <stddef.h>

#pragma STDC FP_CONTRACT OFF /* stock uses non-fused VMLA/VMUL */

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

enum { STOF_NONE = 0, STOF_DECIMAL = 1, STOF_HEX = 2, STOF_INF = 3, STOF_NAN = 4, STOF_NEGATIVE = 8 };

extern int32_t stod_classify_585134(const char **ps, char **endptr);   /* 0x585134 _Stopfx */
extern int32_t stopfx_585258(const char *s0, const char *s, char **endptr,
                             int32_t *px, int32_t maxchunks);           /* 0x585258 _Stoflt */
extern int32_t stoxflt_585410(const char *s0, const char *s, char **endptr,
                              int32_t *px, int32_t maxchunks);          /* 0x585410 _Stoxflt */
extern IAR_VFP float frexpf(float value, int *exponent);               /* 0x59d244 */
extern IAR_VFP float ldexpf(float value, int n);                       /* 0x59d28c */
extern void audio_uart_ring_errno_range_set_439cb2(void);              /* 0x439cb2 errno = ERANGE */

IAR_VFP float iar_strtof_595964(const char *text, char **endptr);

/* ROM 0x59596c: 1e1, 1e2, 1e4, 1e8, 1e16 (the following 1e32 is used as a constant). */
static const uint32_t fdtento_pows_bits[5] = {
    0x41200000u, 0x42c80000u, 0x461c4000u, 0x4cbebc20u, 0x5a0e1bcau};

#define F_BITS_1E32     0x749dc5aeu /* ROM 0x59594c */
#define F_BITS_1EM32    0x0a4fb11eu /* ROM 0x595948 */
#define F_BITS_INF      0x7f800000u /* ROM 0x59595c */
#define F_BITS_NAN      0x7fffffffu /* ROM 0x595960 */
#define F_DEC_CHUNK     1e9f        /* ROM 0x595954 */
#define F_HEX_CHUNK     268435456.0f /* ROM 0x595958 */

static uint32_t float_bits(float value)
{
    union { float f; uint32_t u; } v = { .f = value };
    return v.u;
}

static float bits_float(uint32_t bits)
{
    union { uint32_t u; float f; } v = { .u = bits };
    return v.f;
}

/* +/-0 or +/-Inf (NaN is not). */
static int zero_or_inf(float x)
{
    uint32_t bits = float_bits(x);

    if ((bits << 1) == 0u)
        return 1;
    return ((int32_t)(bits << 1) >> 24) == -1 && (bits << 9) == 0u;
}

/* Stock 0x00595708 (_FDtento) */
static IAR_VFP float fdtento_595708(float x, int32_t n, int32_t *perr)
{
    float factor = 1.0f;
    const uint32_t *p = fdtento_pows_bits;
    int32_t i = 5;
    int xexp;

    if (n == 0 || zero_or_inf(x))
        return x;
    if (n < 0) {
        uint32_t nu = 0u - (uint32_t)n;

        for (; nu != 0u && i != 0; nu >>= 1, ++p, --i)
            if ((nu & 1u) != 0u)
                factor *= bits_float(*p);
        x = frexpf(x, &xexp);
        x = ldexpf(x / factor, xexp);
        if (!zero_or_inf(x) && nu != 0u) {
            do {
                x = frexpf(x, &xexp);
                x = ldexpf(x * bits_float(F_BITS_1EM32), xexp);
                if (zero_or_inf(x))
                    break;
            } while (--nu != 0u);
        }
    } else {
        for (; n > 0 && i != 0; n >>= 1, ++p, --i)
            if ((n & 1) != 0)
                factor *= bits_float(*p);
        x = frexpf(x, &xexp);
        x = ldexpf(x * factor, xexp);
        if (!zero_or_inf(x) && n > 0) {
            do {
                x = frexpf(x, &xexp);
                x = ldexpf(x * bits_float(F_BITS_1E32), xexp);
                if (zero_or_inf(x))
                    break;
            } while (--n > 0);
        }
    }
    if (zero_or_inf(x)) {
        audio_uart_ring_errno_range_set_439cb2();
        if (perr != NULL)
            *perr |= 1;
    }
    return x;
}

static float chunks_to_float(const int32_t *chunks, int32_t n, float radix)
{
    float x = (float)chunks[0];

    for (int32_t i = 1; i < n; i++)
        x = (float)chunks[i] + x * radix;
    return x;
}

/* Stock 0x0059585c (_Stof) */
static IAR_VFP float stof_59585c(const char *s, char **endptr, int32_t pten, int32_t *perr)
{
    const char *s0 = s;
    int32_t lo[4]; /* lo[0] exponent, lo[1..] significand chunks */
    float x;

    if (perr != NULL)
        *perr = 0;
    int32_t code = stod_classify_585134(&s, endptr);
    uint32_t negative = ((uint32_t)code >> 3) & 1u;
    code &= ~STOF_NEGATIVE;

    if (code == STOF_DECIMAL) {
        int32_t n = stopfx_585258(s0, s, endptr, lo, code);
        x = n == 0 ? 0.0f : chunks_to_float(&lo[1], n, F_DEC_CHUNK);
        x = fdtento_595708(x, lo[0] + pten, perr);
    } else if (code == STOF_HEX) {
        int32_t n = stoxflt_585410(s0, s, endptr, lo, 1);
        x = n == 0 ? 0.0f : chunks_to_float(&lo[1], n, F_HEX_CHUNK);
        x = ldexpf(x, lo[0]);
        x = fdtento_595708(x, pten, perr);
    } else if (code == STOF_INF) {
        x = bits_float(F_BITS_INF);
    } else if (code == STOF_NAN) {
        x = bits_float(F_BITS_NAN);
    } else {
        x = 0.0f;
    }
    return negative ? -x : x;
}

/* Stock 0x00595964 (strtof) */
IAR_VFP float iar_strtof_595964(const char *text, char **endptr)
{
    return stof_59585c(text, endptr, 0, NULL);
}
