// SPDX-License-Identifier: MIT
/*
 * C library completions for the open-toolchain G2 build (g2c campaign).
 * Stock links IAR DLib; upstream sources compiled whole here (FreeType, cJSON,
 * LVGL) reference calloc/strncat, which DLib would supply. These are ISO C
 * bodies over the firmware's own malloc, not recovered stock code.
 */
#include <stddef.h>

extern void *malloc(size_t size);
extern void *memset(void *s, int c, size_t n);

void *calloc(size_t nmemb, size_t size)
{
    if (size != 0u && nmemb > (size_t)-1 / size)
        return NULL;
    size_t total = nmemb * size;
    void *p = malloc(total);
    if (p != NULL)
        memset(p, 0, total);
    return p;
}

char *strncat(char *restrict dst, const char *restrict src, size_t n)
{
    char *d = dst;
    while (*d != '\0')
        d++;
    while (n-- != 0u && *src != '\0')
        *d++ = *src++;
    *d = '\0';
    return dst;
}
