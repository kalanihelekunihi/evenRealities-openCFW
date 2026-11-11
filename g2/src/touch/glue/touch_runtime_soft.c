/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>
#include <string.h>

void *memmove(void *dst, const void *src, size_t n)
{
    unsigned char *d = (unsigned char *)dst;
    const unsigned char *s = (const unsigned char *)src;
    if (d < s) {
        while (n--)
            *d++ = *s++;
    } else {
        d += n;
        s += n;
        while (n--)
            *--d = *--s;
    }
    return dst;
}

int memcmp(const void *a, const void *b, size_t n)
{
    const unsigned char *x = (const unsigned char *)a;
    const unsigned char *y = (const unsigned char *)b;
    while (n--) {
        if (*x != *y)
            return (int)*x - (int)*y;
        ++x;
        ++y;
    }
    return 0;
}

size_t strlen(const char *s)
{
    size_t n = 0;
    while (s[n])
        ++n;
    return n;
}

unsigned __aeabi_uidiv(unsigned n, unsigned d)
{
    unsigned q = 0u;
    if (d == 0u)
        return 0u;
    while (n >= d) {
        unsigned t = d, qbit = 1u;
        while (((t << 1) > t) && ((t << 1) <= n)) {
            t <<= 1;
            qbit <<= 1;
        }
        n -= t;
        q += qbit;
    }
    return q;
}

/* RTABI __aeabi_uidivmod: quotient in R0, remainder in R1, i.e. the AAPCS
 * return registers of a 64-bit result. (The former naked body reused R2 as
 * the divisor after the call, but __aeabi_uidiv clobbers R2.) */
unsigned long long __aeabi_uidivmod(unsigned n, unsigned d)
{
    unsigned q = __aeabi_uidiv(n, d);
    unsigned r = n - q * d;
    return ((unsigned long long)r << 32) | q;
}

/* Clang/ARM EABI helpers used by CapSense generator/sensing. */
void __aeabi_memclr4(void *dst, size_t n)
{
    memset(dst, 0, n);
}
void __aeabi_memclr(void *dst, size_t n) __attribute__((alias("__aeabi_memclr4")));
