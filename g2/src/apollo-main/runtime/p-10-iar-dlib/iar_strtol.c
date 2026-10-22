/* IAR DLIB isxdigit, _Stolx and strtol, native 0x595984..0x595a31 (next to the
 * DLIB printf entry 0x595a34).
 *
 * strtol skips locale white space (0x4d58ae), accepts one sign that must not be
 * followed by white space, and delegates digits/base handling to the unsigned
 * parser 0x48d724. An unsigned result outside the signed range sets
 * errno = ERANGE (0x439cb2), raises *perr and saturates to LONG_MIN/LONG_MAX. */
#include <stdint.h>
#include <stddef.h>

extern int32_t audio_uart_ring_locale_space_4d58ae(uint32_t ch); /* isspace */
extern uint32_t iar_stoulx_48d724(const char *s, char **endptr, int32_t base, int32_t *perr);
extern void audio_uart_ring_errno_range_set_439cb2(void); /* errno = ERANGE */

int32_t iar_isxdigit_595984(int32_t c)
{
    if ((uint32_t)(c - 'a') < 6u || (uint32_t)(c - 'A') < 6u)
        return 1;
    return (uint32_t)(c - '0') < 10u;
}

int32_t iar_stolx_5959a2(const char *s, char **endptr, int32_t base, int32_t *perr)
{
    char *local_end;
    if (endptr == NULL)
        endptr = &local_end;
    const char *p = s;
    while (audio_uart_ring_locale_space_4d58ae((uint8_t)*p) != 0)
        p++;
    char sign = *p;
    if (sign == '-' || sign == '+') {
        p++;
        if (audio_uart_ring_locale_space_4d58ae((uint8_t)*p) != 0) {
            *endptr = (char *)s;
            return 0;
        }
    } else {
        sign = '+';
    }
    uint32_t value = iar_stoulx_48d724(p, endptr, base, perr);
    if (p == *endptr) {
        *endptr = (char *)s;
        return 0;
    }
    if (sign == '+') {
        if (value < 0x80000000u)
            return (int32_t)value;
    } else if (sign == '-') {
        if (value <= 0x80000000u)
            return (int32_t)(0u - value);
    } else {
        return (int32_t)value;
    }
    audio_uart_ring_errno_range_set_439cb2();
    if (perr != NULL)
        *perr = 1;
    return sign == '-' ? INT32_MIN : INT32_MAX;
}

int32_t iar_strtol_595a2e(const char *s, char **endptr, int32_t base)
{
    return iar_stolx_5959a2(s, endptr, base, NULL);
}
