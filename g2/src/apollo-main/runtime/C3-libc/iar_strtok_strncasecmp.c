/* IAR DLIB strtok and strncasecmp, reconstructed from the 2.2.6.10 disassembly.
 * IAR DLIB has no public source; these are clean freestanding equivalents.
 *
 * Stock ranges:
 *   0x00594884..0x005948cb  strtok (literal 0x5948cc = RAM 0x20074f0c save pointer)
 *   0x00595f0c..0x00595f4b  strncasecmp (no literal pool)
 *
 * strtok calls strspn 0x541b52 / strcspn 0x541b30 (runtime/iar-runtime/runtime.c);
 * strncasecmp folds both bytes through the locale tolower dispatch 0x4d58c2 and
 * returns -1/1 on the first mismatch, ordered by the low byte of the folded
 * values. Profile g2-apollo-main-2. */
#include <stdint.h>
#include <stddef.h>

extern uint32_t g2_strspn(const uint8_t *s, const uint8_t *set);  /* 0x541b52 strspn */
extern uint32_t g2_strcspn(const uint8_t *s, const uint8_t *set); /* 0x541b30 strcspn */
extern int32_t audio_uart_ring_locale_lower_4d58c2(uint32_t value); /* 0x4d58c2 tolower */

char *g2_strtok_594884(char *s, const char *delim);
int32_t strncasecmp_595f0c(const char *a, const char *b, uint32_t len);

/* RAM 0x20074f0c: strtok continuation pointer (no named object in g2/src). */
#define G2_STRTOK_SAVE (*(char *volatile *)(uintptr_t)0x20074f0cu)

/* Stock 0x00594884 (strtok) */
char *g2_strtok_594884(char *s, const char *delim)
{
    char *end;

    if (s == NULL) {
        s = G2_STRTOK_SAVE;
        if (s == NULL)
            return NULL;
    }
    s += g2_strspn((const uint8_t *)s, (const uint8_t *)delim);
    if (*s == '\0') {
        G2_STRTOK_SAVE = NULL;
        return NULL;
    }
    end = s + g2_strcspn((const uint8_t *)s, (const uint8_t *)delim);
    if (*end != '\0')
        *end++ = '\0';
    G2_STRTOK_SAVE = end;
    return s;
}

/* Stock 0x00595f0c (strncasecmp) */
int32_t strncasecmp_595f0c(const char *a, const char *b, uint32_t len)
{
    if (len == 0u)
        return 0;
    do {
        int32_t ca = audio_uart_ring_locale_lower_4d58c2((uint8_t)*a);
        int32_t cb = audio_uart_ring_locale_lower_4d58c2((uint8_t)*b++);

        if (ca != cb)
            return (uint8_t)ca < (uint8_t)cb ? -1 : 1;
        if (*a++ == '\0')
            return 0;
    } while (--len != 0u);
    return 0;
}
