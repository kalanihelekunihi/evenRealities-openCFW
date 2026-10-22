/* IAR DLIB (EWARM 9.x) isalpha and 64-bit string-to-integer conversions
 * (Dinkumware-derived _Stoullx / _Stollx), firmware 2.2.6.10. IAR DLIB has no
 * public source; this is a freestanding equivalent written from the disassembly.
 *   0x541ba8..0x541bbb  isalpha: tail call through ctype locale slot +0x10
 *   0x541bd8..0x541d83  _Stoullx (s, endptr, base, perr)
 *   0x541d84..0x541d8b  strtoull = _Stoullx(s, endptr, base, NULL)
 *   0x541d8c..0x541e2b  _Stollx (s, endptr, base, perr)
 *   0x541e2c..0x541e33  strtoll  = _Stollx(s, endptr, base, NULL)
 * The 32-bit siblings are runtime/a-12-iar-dlib (_Stoulx 0x48d724) and
 * runtime/p-10-iar-dlib (_Stolx 0x5959a2). */
#include <stdint.h>
#include <stddef.h>

typedef int32_t (*iar_ctype_fn)(int32_t ch);

extern void *iar_ctype_locale_4d43a4(void);                       /* RAM 0x200044c0 ctype table + callbacks */
extern int32_t audio_uart_ring_locale_space_4d58ae(uint32_t ch);  /* isspace */
extern int32_t audio_uart_ring_locale_lower_4d58c2(uint32_t ch);  /* tolower */
extern void *memchr_4d40e0(const void *s, int32_t c, uint32_t n);
extern void audio_uart_ring_errno_range_set_439cb2(void);         /* errno = ERANGE */
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t low, uint32_t high,
                                               uint32_t dlow, uint32_t dhigh); /* __aeabi_uldivmod */

/* xstoull.c tables: maximum significant digits per base (64-bit), then the digit set. */
static const uint8_t ndigs64[37] = {
    0, 0, 65, 41, 33, 28, 25, 23, 22, 21, 20, 19, 18, 18, 17, 17, 17, 16, 16,
    16, 15, 15, 15, 15, 14, 14, 14, 14, 14, 14, 14, 13, 13, 13, 13, 13, 13,
}; /* ROM 0x6f1258 */
static const char digits[] = "0123456789abcdefghijklmnopqrstuvwxyz"; /* ROM 0x6f1280 */

int32_t isalpha_541ba8(int32_t ch);
uint64_t stoull_541bd8(const char *s, char **endptr, int32_t base, int32_t *perr);
uint64_t strtoull_541d84(const char *s, char **endptr, uint32_t base);
int64_t stoll_541d8c(const char *s, char **endptr, int32_t base, int32_t *perr);
int64_t strtoll_541e2c(const char *s, char **endptr, uint32_t base);

int32_t isalpha_541ba8(int32_t ch)
{
    const uintptr_t *locale = (const uintptr_t *)iar_ctype_locale_4d43a4();
    return ((iar_ctype_fn)locale[4])(ch);
}

/* Leading zeros do not count toward ndigs64[base]; an overflow sets
 * errno = ERANGE, *perr = 1 and returns UINT64_MAX without the sign applied. */
uint64_t stoull_541bd8(const char *s, char **endptr, int32_t base, int32_t *perr)
{
    const char *sc;
    const char *s1;
    const char *s2;
    const char *sd;
    char sign;
    uint64_t x = 0u;
    uint64_t y = 0u;
    uint32_t dig = 0u;
    int32_t n;

    if (perr != NULL)
        *perr = 0;
    for (sc = s; audio_uart_ring_locale_space_4d58ae((uint8_t)*sc) != 0; ++sc) {
    }
    if (*sc == '-' || *sc == '+')
        sign = *sc++;
    else
        sign = '+';
    if (base < 0 || base == 1 || base > 36) {
        if (endptr != NULL)
            *endptr = (char *)s;
        return 0u;
    }
    if (base > 0) {
        if (base == 16 && sc[0] == '0' && ((uint8_t)sc[1] | 0x20u) == 'x')
            sc += 2;
    } else if (*sc != '0') {
        base = 10;
    } else if (((uint8_t)sc[1] | 0x20u) == 'x') {
        base = 16;
        sc += 2;
    } else {
        base = 8;
    }
    for (s1 = sc; *sc == '0'; ++sc) {
    }
    for (s2 = sc;
         (sd = (const char *)memchr_4d40e0(digits, audio_uart_ring_locale_lower_4d58c2((uint8_t)*sc),
                                           (uint32_t)base)) != NULL;
         ++sc) {
        y = x;
        dig = (uint8_t)(sd - digits);
        x = x * (uint64_t)(int64_t)base + dig;
    }
    if (s1 == sc) {
        if (endptr != NULL)
            *endptr = (char *)s;
        return 0u;
    }
    n = (int32_t)(sc - s2) - (int32_t)ndigs64[base];
    if (n >= 0) {
        uint64_t prev = x - dig;
        if (n > 0 || x < prev ||
            audio_uart_ring_u64_div_47cc60((uint32_t)prev, (uint32_t)(prev >> 32), (uint32_t)base,
                                           (uint32_t)((int64_t)base >> 32)) != y) {
            audio_uart_ring_errno_range_set_439cb2();
            if (perr != NULL)
                *perr = 1;
            x = UINT64_MAX;
            sign = '+';
        }
    }
    if (sign == '-')
        x = 0u - x;
    if (endptr != NULL)
        *endptr = (char *)sc;
    return x;
}

uint64_t strtoull_541d84(const char *s, char **endptr, uint32_t base)
{
    return stoull_541bd8(s, endptr, (int32_t)base, NULL);
}

/* One sign that must not be followed by white space, then the unsigned
 * parser; out-of-range values set ERANGE, *perr = 1 and saturate. */
int64_t stoll_541d8c(const char *s, char **endptr, int32_t base, int32_t *perr)
{
    char *local_end;
    const char *sc = s;
    char sign;
    uint64_t x;

    if (endptr == NULL)
        endptr = &local_end;
    while (audio_uart_ring_locale_space_4d58ae((uint8_t)*sc) != 0)
        sc++;
    sign = *sc;
    if (sign == '-' || sign == '+') {
        sc++;
        if (audio_uart_ring_locale_space_4d58ae((uint8_t)*sc) != 0) {
            *endptr = (char *)s;
            return 0;
        }
    } else {
        sign = '+';
    }
    x = stoull_541bd8(sc, endptr, base, perr);
    if (sc == *endptr) {
        *endptr = (char *)s;
        return 0;
    }
    if (sign == '+') {
        if (x < 0x8000000000000000u)
            return (int64_t)x;
    } else if (sign == '-') {
        if (x <= 0x8000000000000000u)
            return (int64_t)(0u - x);
    } else {
        return (int64_t)x;
    }
    audio_uart_ring_errno_range_set_439cb2();
    if (perr != NULL)
        *perr = 1;
    return sign == '-' ? INT64_MIN : INT64_MAX;
}

int64_t strtoll_541e2c(const char *s, char **endptr, uint32_t base)
{
    return stoll_541d8c(s, endptr, (int32_t)base, NULL);
}
