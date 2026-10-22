/* IAR DLIB strtod front-end scanners (Dinkumware-derived xstopfx.c / xstoflt.c).
 * IAR DLIB has no public source; this is a clean freestanding equivalent
 * written from the 2.2.6.10 disassembly.
 * Native 0x585134..0x585257 (_Stopfx, kept under the existing name
 * stod_classify_585134) and 0x585258..0x585409 (_Stoflt, kept under the
 * existing name stopfx_585258; constant 0x58540c = 100000000).
 * Both are called only by stodx_542c20 (runtime/iar-dlib-gaps/iar_strtod.c)
 * and sit directly before stoxflt_585410 in stock. No floating point. */
#include <stdint.h>
#include <stddef.h>

enum { STOD_NONE = 0, STOD_DECIMAL = 1, STOD_HEX = 2, STOD_INF = 3, STOD_NAN = 4, STOD_NEGATIVE = 8 };

#define DEC_DIGITS_PER_CHUNK 9
#define DEC_DIGITS_MAX       45
#define EXP_ACCUM_MAX        100000000 /* ROM 0x58540c */

extern int32_t audio_uart_ring_locale_space_4d58ae(uint32_t ch); /* isspace */
extern int32_t isalpha_541ba8(int32_t ch);
extern const uint8_t *iar_locale_4d43a8(void); /* +0x24 -> decimal point string */

int32_t stod_classify_585134(const char **ps, char **endptr);
int32_t stopfx_585258(const char *s0, const char *s, char **endptr, int32_t *px, int32_t maxchunks);

static uint8_t lower(char c)
{
    return (uint8_t)((uint8_t)c | 0x20u);
}

static int is_digit(char c)
{
    return (uint8_t)((uint8_t)c - (uint8_t)'0') < 10u;
}

/* Skips white space and sign, then classifies "nan[(n-char-seq)]", "inf[inity]",
 * "0x<hexdigit>" or plain decimal. *ps always advances past what was consumed
 * (to the digits for decimal and hex); *endptr is written only for NaN/Inf or
 * when "nan"/"inf" did not match (then *ps is restored and STOD_NONE returned).
 * Stock quirk: a NaN result drops the sign bit (code is set to 4, not or-ed). */
int32_t stod_classify_585134(const char **ps, char **endptr)
{
    const char *s = *ps;
    int32_t code = STOD_NONE;

    while (audio_uart_ring_locale_space_4d58ae((uint8_t)*s) != 0)
        s++;
    if (*s == '-') {
        code = STOD_NEGATIVE;
        s++;
    } else if (*s == '+') {
        s++;
    }

    if (lower(*s) == 'n') {
        if (lower(s[1]) == 'a' && lower(s[2]) == 'n') {
            s += 3;
            code = STOD_NAN;
            if (*s == '(') {
                const char *p = s;
                char c;
                do {
                    c = *++p;
                } while (isalpha_541ba8((uint8_t)c) != 0 || is_digit(c) || *p == '_');
                if (*p == ')')
                    s = p + 1;
            }
        } else {
            s = *ps;
            code = STOD_NONE;
        }
    } else if (lower(*s) == 'i') {
        if (lower(s[1]) == 'n' && lower(s[2]) == 'f') {
            s += 3;
            code |= STOD_INF;
            if (lower(s[0]) == 'i' && lower(s[1]) == 'n' && lower(s[2]) == 'i' &&
                lower(s[3]) == 't' && lower(s[4]) == 'y')
                s += 5;
        } else {
            s = *ps;
            code = STOD_NONE;
        }
    } else {
        if (*s == '0' && lower(s[1]) == 'x') {
            const char *p = s + 2;
            if (*p == '.')
                p++;
            uint8_t c = (uint8_t)*p;
            if ((uint8_t)(c - 'a') < 6u || (uint8_t)(c - 'A') < 6u || (uint8_t)(c - '0') < 10u) {
                *ps = s + 2;
                return code | STOD_HEX;
            }
        }
        *ps = s;
        return code | STOD_DECIMAL;
    }

    if (endptr != NULL)
        *endptr = (char *)s;
    *ps = s;
    return code;
}

/* Decimal significand into base-1e9 chunks: px[0] = decimal exponent,
 * px[1..] chunks (most significant first). Keeps at most maxchunks*9 (<= 45)
 * digits, rounding a dropped non-zero digit into the last kept one.
 * Returns the chunk count; *endptr is s0 when no digit was seen. */
int32_t stopfx_585258(const char *s0, const char *s, char **endptr, int32_t *px, int32_t maxchunks)
{
    uint8_t buf[48];
    int32_t nmax = maxchunks * DEC_DIGITS_PER_CHUNK;
    int32_t n = 0;
    int32_t chunk = 0;
    uint8_t sticky = 0u;
    uint8_t seen = 0u;

    if (nmax > DEC_DIGITS_MAX)
        nmax = DEC_DIGITS_MAX;
    px[0] = 0;
    px[1] = 0;
    for (; *s == '0'; s++)
        seen = 1u;
    for (; is_digit(*s); s++) {
        if (n < nmax) {
            buf[n++] = (uint8_t)(*s - '0');
        } else {
            px[0]++;
            if (*s != '0')
                sticky = 1u;
        }
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
    for (; is_digit(*s); s++) {
        if (n < nmax) {
            buf[n++] = (uint8_t)(*s - '0');
            px[0]--;
        } else if (*s != '0') {
            sticky = 1u;
        }
        seen = 1u;
    }
    if (sticky)
        buf[nmax - 1]++;
    for (; n > 0; n--) {
        if (buf[n - 1] != 0u)
            break;
        px[0]++;
    }
    if (n == 0) {
        buf[0] = 0u;
        n = 1;
    }

    if (seen) {
        /* Left-pad so the last digit closes a 9-digit chunk. */
        int32_t k = (n / DEC_DIGITS_PER_CHUNK) * DEC_DIGITS_PER_CHUNK + (DEC_DIGITS_PER_CHUNK - n);
        if (k % DEC_DIGITS_PER_CHUNK != 0)
            chunk = 1;
        for (int32_t i = 0; i < n; i++, k++) {
            if (k % DEC_DIGITS_PER_CHUNK == 0)
                px[++chunk] = buf[i];
            else
                px[chunk] = px[chunk] * 10 + buf[i];
        }
        if (lower(*s) == 'e') {
            const char *mark = s;
            char sign = '+';
            int32_t e = 0;
            uint8_t any = 0u;
            s++;
            if (*s == '+' || *s == '-')
                sign = *s++;
            for (; is_digit(*s); s++) {
                if (e < EXP_ACCUM_MAX)
                    e = e * 10 + (*s - '0');
                any = 1u;
            }
            if (sign == '-')
                e = -e;
            px[0] += e;
            if (!any)
                s = mark;
        }
    }
    if (endptr != NULL)
        *endptr = (char *)(seen ? s : s0);
    return chunk;
}
