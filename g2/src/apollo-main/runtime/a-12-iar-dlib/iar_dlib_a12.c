/* IAR DLIB string/number helpers linked into Apollo main.
 * Native 0x48d4e8..0x48d558 (strnlen, strcpy) and 0x48d724..0x48d872
 * (_Stoulx, atoi, atol); the strtoul tail 0x48d874 is
 * drivers/peripherals/ring-unsigned, _Stolx/strtol are runtime/p-10-iar-dlib.
 *
 * strnlen and strcpy are DLIB assembly in stock (word-at-a-time scan,
 * post-indexed copy); the C here is behaviour-equivalent only. atoi
 * (0x48d868, "b 0x48d86c") and atol (0x48d86c) reach _Stoulx(s, NULL, 10,
 * NULL) through shared IAR tail branches 0x48d866 -> 0x48d876. */
#include <stdint.h>
#include <stddef.h>

extern int32_t audio_uart_ring_locale_space_4d58ae(uint32_t ch); /* isspace */
extern int32_t audio_uart_ring_locale_lower_4d58c2(uint32_t ch); /* tolower */
extern void *memchr_4d40e0(const void *s, int32_t c, uint32_t n);
extern void audio_uart_ring_errno_range_set_439cb2(void);        /* errno = ERANGE */

/* xstoul.c tables: maximum significant digits per base, then the digit set. */
static const uint8_t ndigs[37] = {
    0, 0, 33, 21, 17, 14, 13, 12, 11, 11, 10, 10, 9, 9, 9, 9, 9, 8, 8,
    8, 8, 8, 8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
}; /* ROM 0x6f1208 */
static const char digits[] = "0123456789abcdefghijklmnopqrstuvwxyz"; /* ROM 0x6f1230 */

uint32_t strnlen_48d4e8(const char *s, uint32_t max);
char *g2_strcpy_48d540(char *dst, const char *src);
uint32_t iar_stoulx_48d724(const char *s, char **endptr, int32_t base, int32_t *perr);
int32_t atoi_48d868(const char *s);
int32_t atol_48d86c(const char *s);

/* 0x48d4e8: a NULL string has length 0. */
uint32_t strnlen_48d4e8(const char *s, uint32_t max)
{
    uint32_t n = 0u;

    if (s == NULL)
        return 0u;
    while (n < max && s[n] != '\0')
        n++;
    return n;
}

/* 0x48d540 */
char *g2_strcpy_48d540(char *dst, const char *src)
{
    char *out = dst;
    char c = *src++;

    for (;;) {
        *out = c;
        if (c == '\0')
            break;
        c = *src++;
        out++;
    }
    return dst;
}

/* 0x48d724: _Stoulx. Leading zeros do not count toward ndigs[base]; an
 * overflow sets errno = ERANGE, *perr = 1 and returns ULONG_MAX without the
 * sign applied. */
uint32_t iar_stoulx_48d724(const char *s, char **endptr, int32_t base, int32_t *perr)
{
    const char *sc;
    const char *s1;
    const char *s2;
    const char *sd;
    char sign;
    uint32_t x = 0u;
    uint32_t y = 0u;
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
        x = x * (uint32_t)base + dig;
    }
    if (s1 == sc) {
        if (endptr != NULL)
            *endptr = (char *)s;
        return 0u;
    }
    n = (int32_t)(sc - s2) - (int32_t)ndigs[base];
    if (n < 0 || (n == 0 && x >= dig && (x - dig) / (uint32_t)base == y)) {
        if (sign == '-')
            x = 0u - x;
    } else {
        audio_uart_ring_errno_range_set_439cb2();
        if (perr != NULL)
            *perr = 1;
        x = UINT32_MAX;
    }
    if (endptr != NULL)
        *endptr = (char *)sc;
    return x;
}

/* 0x48d868 */
int32_t atoi_48d868(const char *s)
{
    return atol_48d86c(s);
}

/* 0x48d86c */
int32_t atol_48d86c(const char *s)
{
    return (int32_t)iar_stoulx_48d724(s, NULL, 10, NULL);
}
