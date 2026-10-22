/* IAR DLIB formatted-input engine (Dinkumware-derived _Scanf and _Getstr).
 * The original is IAR DLIB (EWARM 9.x), which has no public source; this is a
 * clean freestanding equivalent written from the 2.2.6.10 disassembly.
 * Native scanf_core_4d1638 0x4d1638..0x4d2111 (literals 0x4d20fc..0x4d210b),
 * getstr_4d2158 0x4d2158..0x4d22fb (constants 0x4d22fc..0x4d2367).
 *
 * Out-of-line helpers of the same module already in g2/src: g2_getn (0x4d15fa)
 * and g2_ungetn (0x4d161c) in runtime/iar-runtime, g2_ranmatch (0x4d2112).
 * sscanf (0x475fc0) is audio_ble_parse_version in ble/ble-format; it still calls
 * the bounded audio_ble_scan_core reduction and should call scanf_core_4d1638.
 *
 * Return value: the conversion count; 0 when the input stops matching before
 * the first conversion (also for an EOF on a literal), -1 for an input failure
 * before the first conversion, and -1 - 34 when a NULL destination trips the
 * C11 constraint handler (scanf_s, secure != 0, returns -1 instead). */
#include <stdint.h>
#include <stddef.h>

#define EOF_CH (-1)
#define WIDTH_MAX 0x0ccccccbu      /* ROM 0x4d2100: stop accumulating the field width */
#define NGET_UNLIMITED 0x7fffffff
#define NGET_INT_UNLIMITED 0x7ffffffe /* ROM 0x4d22fc: integer path reads its first char unchecked */
#define FLOAT_DIGITS_MAX 36
#define FLOAT_EXP_DIGITS_MAX 8
#define CONSTRAINT_EINVAL_RANGE 34

typedef int32_t (*iar_scan_get_t)(void *arg, int32_t ch, uint32_t advance); /* advance 0 = push back ch */

/* _Sft scan state (32 bytes, on the engine's stack). */
typedef struct {
    void *arg;              /* +0x00 callback context */
    uint32_t *ap;           /* +0x04 argument cursor */
    const uint8_t *s;       /* +0x08 format position */
    int32_t nchar;          /* +0x0c characters consumed (%n) */
    int32_t nget;           /* +0x10 characters left in this field */
    int32_t width;          /* +0x14 field width, 0 = none */
    uint32_t size;          /* +0x18 scanf_s buffer size, UINT32_MAX when none */
    uint8_t noconv;         /* +0x1c '*' assignment suppression */
    uint8_t qual;           /* +0x1d h j l t z L, 'b' = hh, 'q' = ll */
    uint8_t stored;         /* +0x1e this conversion assigned */
    uint8_t secure;         /* +0x1f scanf_s */
} iar_scan_state_t;
_Static_assert(sizeof(iar_scan_state_t) == 32, "stock _Sft size");

extern int32_t g2_getn(iar_scan_get_t get, iar_scan_state_t *px);            /* 0x4d15fa */
extern void g2_ungetn(iar_scan_get_t get, iar_scan_state_t *px, int32_t ch);  /* 0x4d161c */
extern int32_t g2_ranmatch(const uint8_t *set, int32_t ch, uint32_t n);       /* 0x4d2112 */
extern int32_t scan_get_counted_4d15e8(iar_scan_get_t get, iar_scan_state_t *px); /* ++nchar, get */
extern int32_t audio_uart_ring_locale_space_4d58ae(uint32_t ch);               /* isspace */
extern int32_t isalpha_541ba8(int32_t ch);                                     /* locale slot +0x10 */
extern const uint8_t *iar_locale_4d43a8(void);   /* RAM 0x20004488; +0x24 -> decimal point string */
extern char *strchr_481818(const char *s, int32_t c);   /* also matches the terminator */
extern void *memchr_4d40e0(const void *s, int32_t c, uint32_t n);
extern uint32_t constraint_handler_call_4d40a0(const char *message);
extern __attribute__((pcs("aapcs"))) double strtod_541bc2(const char *s, char **endptr, int32_t pten, int32_t *perr); /* stodx_542c20 */
extern __attribute__((pcs("aapcs"))) double ldexp_4d41f4(double x, int32_t exp);
extern __attribute__((pcs("aapcs"))) float double_to_float_541bca(double x);
extern uint64_t strtoull_541d84(const char *s, char **endptr, uint32_t base);
extern int64_t strtoll_541e2c(const char *s, char **endptr, uint32_t base);

int32_t getstr_4d2158(iar_scan_get_t get, iar_scan_state_t *px, int32_t sfl);

static const char qualifiers[] = "hjltzL";          /* ROM 0x4d2104 */
static const char no_skip_conversions[] = "cCn[";   /* ROM 0x4d2300 */
static const char bad_n_arg[] = "scanf_s: bad %n argument";        /* ROM 0x4d2308 */
static const char bad_str_size[] = "scanf_s: bad %c, %s, or %[ size"; /* ROM 0x4d2324 */
static const char bad_int_arg[] = "scanf_s: bad integer argument";  /* ROM 0x4d2344 */
static const char bad_str_arg[] = "scanf_s: bad %c, %s, or %[ argument"; /* ROM 0x75d3a4 */
static const char bad_float_arg[] = "scanf_s: bad floating-point argument"; /* ROM 0x7514cc */

#define GET(px) ((px)->nchar++, get((px)->arg, 0, 1u))
#define GETN(px) (--(px)->nget >= 0 ? GET(px) : ((px)->nchar++, EOF_CH))

static uint32_t digit_value(int32_t ch)
{
    uint32_t c = (uint8_t)ch;
    if (c >= 'a')
        return (uint8_t)(ch - 87);
    if (c >= 'A')
        return (uint8_t)(ch - 55);
    if (c - '0' < 10u)
        return (uint8_t)(ch - '0');
    return 0xffu;
}

static uint32_t next_arg(iar_scan_state_t *px)
{
    return *px->ap++;
}

static int32_t constraint(const char *message)
{
    return -1 - (int32_t)constraint_handler_call_4d40a0(message);
}

/* Store a converted integer per the length qualifier; 0 on success. */
static int32_t store_integer(iar_scan_state_t *px, uint64_t value, int32_t is_pointer)
{
    void *dst = (void *)(uintptr_t)next_arg(px);
    if (dst == NULL)
        return constraint(bad_int_arg);
    if (is_pointer) {
        *(uint32_t *)dst = (uint32_t)value;
        return 0;
    }
    switch (px->qual) {
    case 'b': *(uint8_t *)dst = (uint8_t)value; break;
    case 'h': *(uint16_t *)dst = (uint16_t)value; break;
    case 'j':
    case 'q': *(uint64_t *)dst = value; break;
    default: *(uint32_t *)dst = (uint32_t)value; break; /* l t z and none */
    }
    return 0;
}

/* %d %i %o %u %x %X %p. Returns 1 converted, 0 matching failure, -1 input failure,
 * or a constraint result. */
static int32_t scan_integer(iar_scan_get_t get, iar_scan_state_t *px)
{
    char buf[32];
    char *p = buf;
    char *const end = buf + 31;
    uint32_t base = 0u;
    uint8_t seen = 0u;
    int32_t ch;
    uint8_t conv = *px->s;

    px->nget = px->width > 0 ? px->width - 1 : NGET_INT_UNLIMITED;
    if (px->nget < 0) {
        px->nchar++;
        ch = EOF_CH;
    } else {
        ch = GET(px);
        if (ch == '+' || ch == '-') {
            *p++ = (char)ch;
            ch = GETN(px);
        }
    }
    if (conv == 'd' || conv == 'u')
        base = 10u;
    else if (conv == 'i')
        base = 0u;
    else if (conv == 'o')
        base = 8u;
    else if (conv == 'p' || (conv | 0x20u) == 'x')
        base = 16u;

    if (ch == '0') {
        seen = 1u;
        ch = GETN(px);
        if ((uint8_t)((uint32_t)ch | 0x20u) == 'x') {
            if (base == 0u || base == 16u) {
                base = 16u;
                if (--px->nget < 0) {
                    px->nchar++;
                    g2_ungetn(get, px, EOF_CH);
                    return p == buf ? -1 : 0; /* "0x" cut off by the width: no digits */
                }
                ch = GET(px);
                seen = 0u;
            }
        } else if (base == 0u) {
            base = 8u;
        }
        while (ch == '0') {
            ch = --px->nget >= 0 ? scan_get_counted_4d15e8(get, px) : (px->nchar++, EOF_CH);
            seen = 1u;
        }
        if (seen)
            *p++ = '0';
    } else if (base == 0u) {
        base = 10u;
    }

    for (;;) {
        if (ch == EOF_CH || digit_value(ch) >= (uint8_t)base)
            break;
        if (p < end)
            *p++ = (char)ch;
        seen = 1u;
        if (--px->nget < 0) {
            px->nchar++;
            ch = EOF_CH;
            break;
        }
        ch = GET(px);
    }
    g2_ungetn(get, px, ch);
    if (!seen)
        return (p == buf && ch == EOF_CH) ? -1 : 0;
    *p = '\0';
    if (px->noconv)
        return 1;

    uint64_t value;
    if (conv == 'd' || conv == 'i')
        value = (uint64_t)strtoll_541e2c(buf, NULL, base);
    else
        value = strtoull_541d84(buf, NULL, base);
    px->stored = 1u;
    int32_t status = store_integer(px, value, conv == 'p');
    return status != 0 ? status : 1;
}

/* %a %e %f %g (and upper case): collect the field into buf, then strtod. */
static int32_t scan_float(iar_scan_get_t get, iar_scan_state_t *px)
{
    char buf[64];
    char *p = buf;
    int32_t pten = 0;
    uint32_t base = 10u;
    int32_t count = 0;
    uint8_t seen = 0u;
    uint8_t zero;
    int32_t ch;

    px->nget = px->width > 0 ? px->width : NGET_UNLIMITED;
    ch = g2_getn(get, px);
    if (ch == '+' || ch == '-') {
        *p++ = (char)ch;
        ch = g2_getn(get, px);
    }

    if (ch == '0') {
        ch = g2_getn(get, px);
        if ((uint8_t)((uint32_t)ch | 0x20u) == 'x') {
            *p++ = '0';
            *p++ = 'x';
            ch = g2_getn(get, px);
            base = 16u;
            zero = 0u;
        } else {
            zero = 1u;
        }
        while (ch == '0') {
            ch = --px->nget >= 0 ? scan_get_counted_4d15e8(get, px) : (px->nchar++, EOF_CH);
            zero = 1u;
        }
        seen = zero;
        if (zero)
            *p++ = '0';
    } else if ((uint8_t)((uint32_t)ch | 0x20u) == 'n') {
        /* nan or nan(n-char-sequence) */
        *p++ = 'n';
        ch = g2_getn(get, px);
        if ((uint8_t)((uint32_t)ch | 0x20u) != 'a')
            goto unget_fail;
        *p++ = 'a';
        ch = g2_getn(get, px);
        if ((uint8_t)((uint32_t)ch | 0x20u) != 'n')
            goto unget_fail;
        ch = g2_getn(get, px);
        if (ch != '(') {
            g2_ungetn(get, px, ch);
            *p++ = 'n';
            goto convert;
        }
        do {
            ch = --px->nget >= 0 ? scan_get_counted_4d15e8(get, px) : (px->nchar++, EOF_CH);
        } while (isalpha_541ba8(ch) || (uint32_t)(ch - '0') < 10u || ch == '_');
        if (ch != ')')
            goto unget_fail;
        *p++ = 'n';
        goto convert;
    } else if ((uint8_t)((uint32_t)ch | 0x20u) == 'i') {
        /* inf or infinity */
        *p++ = 'i';
        ch = g2_getn(get, px);
        if ((uint8_t)((uint32_t)ch | 0x20u) != 'n')
            goto unget_fail;
        *p++ = 'n';
        ch = g2_getn(get, px);
        if ((uint8_t)((uint32_t)ch | 0x20u) != 'f')
            goto unget_fail;
        ch = g2_getn(get, px);
        if ((uint8_t)((uint32_t)ch | 0x20u) != 'i') {
            g2_ungetn(get, px, ch);
            *p++ = 'f';
            goto convert;
        }
        static const char inity[] = "nity";
        for (const char *q = inity; *q != '\0'; q++) {
            ch = GETN(px);
            if ((uint8_t)((uint32_t)ch | 0x20u) != (uint8_t)*q)
                goto unget_fail;
        }
        *p++ = 'f';
        goto convert;
    }

    /* Integer digits; beyond 36 digits only the decimal exponent grows. */
    for (;;) {
        if (ch == EOF_CH || digit_value(ch) >= (uint8_t)base)
            break;
        if (count < FLOAT_DIGITS_MAX) {
            *p++ = (char)ch;
            count++;
        } else {
            pten++;
        }
        ch = --px->nget >= 0 ? scan_get_counted_4d15e8(get, px) : (px->nchar++, EOF_CH);
        seen = 1u;
    }
    {
        const char *dp = *(const char *const *)(const void *)(iar_locale_4d43a8() + 0x24);
        if (ch == (uint8_t)dp[0]) {
            *p++ = (char)ch;
            ch = GETN(px);
        }
    }
    if (count == 0) {
        while (ch == '0') {
            pten--;
            ch = --px->nget >= 0 ? scan_get_counted_4d15e8(get, px) : (px->nchar++, EOF_CH);
            seen = 1u;
        }
        if (pten < 0) {
            *p++ = '0';
            pten++;
        }
    }
    /* Fraction digits. */
    for (;;) {
        if (ch == EOF_CH || digit_value(ch) >= (uint8_t)base)
            break;
        if (count < FLOAT_DIGITS_MAX) {
            *p++ = (char)ch;
            count++;
        }
        ch = --px->nget >= 0 ? scan_get_counted_4d15e8(get, px) : (px->nchar++, EOF_CH);
        seen = 1u;
    }
    if (!seen)
        goto unget_fail;
    {
        uint8_t e = (uint8_t)((uint32_t)ch | 0x20u);
        if (base == 10u ? e != 'e' : e != 'p') {
            g2_ungetn(get, px, ch);
            goto convert;
        }
    }
    /* Exponent: sign, leading zeros folded to one '0', at most 8 digits kept. */
    *p++ = (char)ch;
    ch = GETN(px);
    if (ch == '+' || ch == '-') {
        *p++ = (char)ch;
        ch = GETN(px);
    }
    seen = 0u;
    while (ch == '0') {
        ch = --px->nget >= 0 ? scan_get_counted_4d15e8(get, px) : (px->nchar++, EOF_CH);
        seen = 1u;
    }
    if (seen)
        *p++ = '0';
    count = 0;
    while ((uint32_t)(ch - '0') < 10u) {
        if (count < FLOAT_EXP_DIGITS_MAX) {
            *p++ = (char)ch;
            count++;
        }
        ch = --px->nget >= 0 ? scan_get_counted_4d15e8(get, px) : (px->nchar++, EOF_CH);
        seen = 1u;
    }
    if (!seen)
        goto unget_fail;
    g2_ungetn(get, px, ch);

convert:
    *p = '\0';
    if (px->noconv)
        return 1;
    double value;
    if (base > 10u)
        value = ldexp_4d41f4(strtod_541bc2(buf, NULL, 0, NULL), pten * 4);
    else
        value = strtod_541bc2(buf, NULL, pten, NULL);
    px->stored = 1u;
    {
        void *dst = (void *)(uintptr_t)next_arg(px);
        if (dst == NULL)
            return constraint(bad_float_arg);
        if (px->qual == 'l' || px->qual == 'L')
            *(double *)dst = value;
        else
            *(float *)dst = double_to_float_541bca(value);
    }
    return 1;

unget_fail:
    g2_ungetn(get, px, ch);
    return (p == buf && ch == EOF_CH) ? -1 : 0;
}

int32_t scanf_core_4d1638(iar_scan_get_t get, void *arg, const char *format,
                          uint32_t **cursor, uint32_t secure)
{
    iar_scan_state_t sft;
    iar_scan_state_t *const px = &sft;
    int32_t nconv = -1;
    int32_t ch;
    int32_t result;

    px->arg = arg;
    px->ap = *cursor;
    px->s = (const uint8_t *)format;
    px->nchar = 0;
    px->secure = (uint8_t)secure;

    for (;; px->s++) {
        while (audio_uart_ring_locale_space_4d58ae(*px->s)) {
            do {
                ch = GET(px);
            } while (audio_uart_ring_locale_space_4d58ae((uint32_t)ch));
            g2_ungetn(get, px, ch);
            px->s++;
        }
        if (*px->s == '\0')
            return nconv > 0 ? nconv : 0;
        if (*px->s != '%') {
            ch = GET(px);
            if (ch == *px->s)
                continue;
            g2_ungetn(get, px, ch);
            return nconv > 0 ? nconv : 0;
        }

        px->s++;
        if (*px->s == '*') {
            px->noconv = '*';
            px->s++;
        } else {
            px->noconv = 0u;
        }
        px->width = 0;
        for (; (uint32_t)(*px->s - '0') < 10u; px->s++) {
            if (px->width < (int32_t)WIDTH_MAX)
                px->width = px->width * 10 + (*px->s - '0');
        }
        px->size = UINT32_MAX;
        px->qual = 0u;
        if (strchr_481818(qualifiers, *px->s) != NULL)
            px->qual = *px->s++;
        if (px->qual == 'h' && *px->s == 'h') {
            px->qual = 'b';
            px->s++;
        } else if (px->qual == 'l' && *px->s == 'l') {
            px->qual = 'q';
            px->s++;
        }
        if (strchr_481818(no_skip_conversions, *px->s) == NULL) {
            do {
                ch = GET(px);
            } while (audio_uart_ring_locale_space_4d58ae((uint32_t)ch));
            g2_ungetn(get, px, ch);
        }
        px->stored = 0u;

        switch (*px->s) {
        case '%':
            ch = GET(px);
            if (ch == '%') {
                result = 1;
                break;
            }
            g2_ungetn(get, px, ch);
            result = ch == EOF_CH ? -1 : 0;
            break;
        case 'A': case 'E': case 'F': case 'G':
        case 'a': case 'e': case 'f': case 'g':
            result = scan_float(get, px);
            break;
        case 'X': case 'd': case 'i': case 'o': case 'p': case 'u': case 'x':
            result = scan_integer(get, px);
            break;
        case '[':
            result = getstr_4d2158(get, px, -1);
            break;
        case 'c':
            result = getstr_4d2158(get, px, 0);
            break;
        case 's':
            result = getstr_4d2158(get, px, 1);
            break;
        case 'n':
            result = 1;
            if (!px->noconv) {
                void *dst = (void *)(uintptr_t)next_arg(px);
                if (dst == NULL) {
                    result = constraint(bad_n_arg);
                    break;
                }
                switch (px->qual) {
                case 'b': *(uint8_t *)dst = (uint8_t)px->nchar; break;
                case 'h': *(uint16_t *)dst = (uint16_t)px->nchar; break;
                case 'j':
                case 'q': *(int64_t *)dst = px->nchar; break;
                default: *(int32_t *)dst = px->nchar; break;
                }
            }
            break;
        default:
            result = 0;
            break;
        }

        if (result > 0) {
            if (nconv < 0)
                nconv = 0;
            if (px->stored)
                nconv++;
            continue;
        }
        if (secure != 0u && result == -1 - CONSTRAINT_EINVAL_RANGE)
            return -1;
        if (nconv < 0)
            nconv = result;
        return nconv;
    }
}

/* %[ (sfl < 0), %c (sfl == 0) and %s (sfl > 0). Returns 1 converted, 0 matching
 * failure, -1 input failure or full scanf_s buffer, or a constraint result. */
int32_t getstr_4d2158(iar_scan_get_t get, iar_scan_state_t *px, int32_t sfl)
{
    const uint8_t *set = NULL;
    uint32_t nset = 0u;
    uint8_t comp = 0u;
    uint8_t ranges = 0u;
    uint8_t *dst = NULL;
    int32_t state = 0; /* 2 after a character was accepted, 1 when the buffer filled */
    int32_t ch;

    if (sfl < 0) {
        const uint8_t *t;
        px->s++;
        if (*px->s == '^') {
            comp = *px->s++;
        }
        set = px->s;
        t = (const uint8_t *)strchr_481818((const char *)(*set == ']' ? set + 1 : set), ']');
        if (t == NULL)
            return 0;
        nset = (uint32_t)(t - set);
        px->s = t;
        if (nset >= 3u && memchr_4d40e0(set + 1, '-', nset - 2u) != NULL)
            ranges = 1u;
    }
    px->nget = px->width > 0 ? px->width : (sfl != 0 ? NGET_UNLIMITED : 1);
    if (!px->noconv) {
        dst = (uint8_t *)(uintptr_t)next_arg(px);
        if (dst == NULL)
            return constraint(bad_str_arg);
        if (px->secure) {
            uint32_t size = next_arg(px);
            if (size >= 0x80000000u)
                return constraint(bad_str_size);
            px->size = size > px->size ? px->size : size;
        }
    }

    for (;;) {
        px->nchar++;
        if (--px->nget < 0) {
            ch = EOF_CH;
            break;
        }
        ch = get(px->arg, 0, 1u);
        if (ch == EOF_CH)
            break;
        if (sfl > 0) {
            if (audio_uart_ring_locale_space_4d58ae((uint32_t)ch))
                break;
        } else if (sfl < 0) {
            int32_t in_set = ranges ? g2_ranmatch(set, ch, nset)
                                    : memchr_4d40e0(set, ch, nset) != NULL;
            if (comp ? in_set : !in_set)
                break;
        }
        if (!px->noconv) {
            if (px->size == 0u) {
                state = 1;
                break;
            }
            *dst++ = (uint8_t)ch;
            px->stored = 1u;
            px->size--;
        }
        state = 2;
    }
    g2_ungetn(get, px, ch);

    if (sfl != 0 && state == 2) {
        if (px->noconv)
            return 1;
        if (px->size == 0u)
            return 0;
        *dst = '\0';
        return 1;
    }
    if (state == 2)
        return 1;
    if ((state & 1) || ch == EOF_CH)
        return -1;
    return 0;
}
