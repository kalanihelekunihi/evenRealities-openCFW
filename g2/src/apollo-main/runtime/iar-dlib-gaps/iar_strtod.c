/* IAR DLIB strtod core (Dinkumware-derived _Stodx and _Stoxflt).
 * The original is IAR DLIB (EWARM 9.x), which has no public source; this is a
 * clean freestanding equivalent written from the 2.2.6.10 disassembly.
 * Native stodx_542c20 0x542c20..0x542d0b (constants 0x542d1c..0x542d43) and
 * stoxflt_585410 0x585410..0x5855e3 (constants 0x5855e4..0x585617).
 * Floating point: build with profile g2-apollo-main-3. Stock stodx_542c20 returns
 * in d0 (VFP ABI); the softfp wrapper strtod_541bc2 moves it to r0:r1. */
#include <stdint.h>
#include <stddef.h>

#define STOD_CHUNKS 2
#define HEX_DIGITS_PER_CHUNK 7
#define HEX_DIGITS_MAX 35
#define EXP_ACCUM_MAX 100000000 /* ROM 0x5855e4 */

enum { STOD_NONE = 0, STOD_DECIMAL = 1, STOD_HEX = 2, STOD_INF = 3, STOD_NAN = 4, STOD_NEGATIVE = 8 };

/* Skips white space, sign and 0x; returns STOD_* with bit 3 set for a minus sign. */
extern int32_t stod_classify_585134(const char **ps, char **endptr); /* _Stopfx: writes *endptr on NaN/Inf/no-match */
/* Decimal digits into 9-digit chunks: px[0] = decimal exponent, px[1..] chunks. */
extern int32_t stopfx_585258(const char *s0, const char *s, char **endptr, int32_t *px, int32_t maxchunks);
extern __attribute__((pcs("aapcs-vfp"))) double dtento_542a80(double x, int32_t n, int32_t *perr); /* x * 10^n with range check; d0 in/out */
extern __attribute__((pcs("aapcs-vfp"))) double dscale_4d4208(double x, int32_t exp); /* x * 2^exp; stock takes x in d0, exp in r0 */
extern void *memchr_4d40e0(const void *s, int32_t c, uint32_t n);
extern const uint8_t *iar_locale_4d43a8(void); /* +0x24 -> decimal point string */

int32_t stoxflt_585410(const char *s0, const char *s, char **endptr, int32_t *px, int32_t maxchunks);

static const char hex_digits[] = "0123456789abcdefABCDEF"; /* ROM 0x5855e8 */
static const uint8_t hex_values[22] = {                     /* ROM 0x585600 */
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 10, 11, 12, 13, 14, 15};

static double bits_to_double(uint64_t bits)
{
    double d;
    __builtin_memcpy(&d, &bits, sizeof d);
    return d;
}

static double chunks_to_double(const int32_t *chunks, int32_t n, double radix)
{
    double d = (double)chunks[0];
    for (int32_t i = 1; i < n; i++)
        d = (double)chunks[i] + d * radix;
    return d;
}

__attribute__((pcs("aapcs-vfp"))) double stodx_542c20(const char *s, char **endptr, int32_t pten, int32_t *perr)
{
    const char *start = s;
    int32_t px[1 + STOD_CHUNKS + 1];
    double d;

    if (perr != NULL)
        *perr = 0;
    int32_t code = stod_classify_585134(&s, endptr);
    uint32_t negative = ((uint32_t)code >> 3) & 1u;
    code &= ~STOD_NEGATIVE;

    if (code == STOD_DECIMAL) {
        int32_t n = stopfx_585258(start, s, endptr, px, STOD_CHUNKS);
        d = n == 0 ? 0.0 : chunks_to_double(&px[1], n, 1e9);
        d = dtento_542a80(d, px[0] + pten, perr);
    } else if (code == STOD_HEX) {
        int32_t n = stoxflt_585410(start, s, endptr, px, STOD_CHUNKS);
        d = n == 0 ? 0.0 : chunks_to_double(&px[1], n, 268435456.0);
        d = dscale_4d4208(d, px[0]);
        d = dtento_542a80(d, pten, perr);
    } else if (code == STOD_INF) {
        d = bits_to_double(0x7ff0000000000000ull);
    } else if (code == STOD_NAN) {
        d = bits_to_double(0x7fffffffffffffffull);
    } else {
        d = 0.0;
    }
    return negative ? -d : d;
}

/* Hex significand into 28-bit chunks: px[0] = binary exponent, px[1..] chunks.
 * Returns the chunk count; *endptr is s0 when no digit was seen. */
int32_t stoxflt_585410(const char *s0, const char *s, char **endptr, int32_t *px, int32_t maxchunks)
{
    uint8_t buf[40];
    int32_t nmax = maxchunks * HEX_DIGITS_PER_CHUNK;
    int32_t n = 0;
    int32_t chunk = 0;
    uint8_t seen = 0u;
    const char *hit;
    const char *end;

    if (nmax > HEX_DIGITS_MAX)
        nmax = HEX_DIGITS_MAX;
    px[0] = 0;
    px[1] = 0;
    for (; *s == '0'; s++)
        seen = 1u;
    while ((hit = memchr_4d40e0(hex_digits, (uint8_t)*s, 22u)) != NULL) {
        if (nmax < n)
            px[0]++;
        else
            buf[n++] = hex_values[hit - hex_digits];
        s++;
        seen = 1u;
    }
    {
        const char *dp = *(const char *const *)(const void *)(iar_locale_4d43a8() + 0x24);
        if (*s == dp[0])
            s++;
    }
    if (n == 0) {
        for (; *s == '0'; s++) {
            px[0]--;
            seen = 1u;
        }
    }
    while ((hit = memchr_4d40e0(hex_digits, (uint8_t)*s, 22u)) != NULL) {
        if (n <= nmax) {
            buf[n++] = hex_values[hit - hex_digits];
            px[0]--;
        }
        s++;
        seen = 1u;
    }
    if (nmax < n) {
        if (buf[nmax] > 7u) /* round half up, no carry propagation */
            buf[nmax - 1]++;
        n = nmax;
        px[0]++;
    }
    for (; n > 0; n--) {
        if (buf[n - 1] != 0u)
            break;
        px[0]++;
    }
    if (n == 0) {
        buf[0] = 0u;
        n = 1;
    }
    px[0] <<= 2;

    end = s;
    if (seen) {
        int32_t phase = (n / HEX_DIGITS_PER_CHUNK) * HEX_DIGITS_PER_CHUNK + (HEX_DIGITS_PER_CHUNK - n);
        if (phase % HEX_DIGITS_PER_CHUNK != 0)
            chunk = 1;
        for (int32_t i = 0; i < n; i++, phase++) {
            if (phase % HEX_DIGITS_PER_CHUNK == 0)
                px[++chunk] = buf[i];
            else
                px[chunk] = (int32_t)buf[i] + px[chunk] * 16;
        }
        if ((*s | 0x20) == 'p') {
            const char *q = s + 1;
            char sign = '+';
            int32_t e = 0;
            uint8_t digits = 0u;
            if (*q == '+' || *q == '-')
                sign = *q++;
            for (; (uint32_t)((uint8_t)*q - '0') < 10u; q++) {
                if (e < EXP_ACCUM_MAX)
                    e = e * 10 + (*q - '0');
                digits = 1u;
            }
            if (sign == '-')
                e = -e;
            px[0] += e;
            end = digits ? q : s;
        }
    }
    if (endptr != NULL)
        *endptr = (char *)(uintptr_t)(seen ? end : s0);
    return chunk;
}
