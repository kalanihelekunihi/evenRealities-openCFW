/* SPDX-License-Identifier: MIT
 * Byte-loop runtime providers for the locked touch image.
 */
#include <stddef.h>

void *memset(void *dst, int c, size_t n)
{
    unsigned char *p = dst;
    unsigned char *end = p + n;
    while (p != end)
        *p++ = (unsigned char)c;
    return dst;
}

void *memcpy(void *dst, const void *src, size_t n)
{
    char *d = dst;
    const char *s = src;
    void *original = dst;
    while (n--)
        *d++ = *s++;
    return original;
}

void __aeabi_memcpy4(void *dst, const void *src, size_t n)
    __attribute__((alias("memcpy")));
void __aeabi_memcpy(void *dst, const void *src, size_t n)
    __attribute__((alias("memcpy")));
