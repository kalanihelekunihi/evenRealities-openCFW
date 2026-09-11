/* SPDX-License-Identifier: MIT */
/*
 * Reviewed C-library leaf routines for the GX8002 UART boot stage 2 (IRAM)
 * image. This stage links its own private copies of strcmp/strchr/strlen/
 * strnlen distinct from the main-image occurrences already covered by
 * runtime_gx8002_memset.c and runtime_gx8002_memcpy.c (different package
 * offsets, different compiled bodies). No klibc/newlib source for these four
 * symbols is present in the pinned NationalChip lvp_kws checkout (only
 * memset.c and prebuilt csky object files are tracked there), so these are clean-room
 * reimplementations reviewed against the decoded stock control flow, not a
 * copy of retained bytes. See docs/research/gx8002-stage2-libc-source.md.
 */
#include <stddef.h>

int open_cfw_gx8002_stage2_strcmp(const char *a, const char *b)
{
    unsigned char ca, cb;
    do {
        ca = (unsigned char)*a++;
        cb = (unsigned char)*b++;
    } while (ca != 0 && ca == cb);
    return (int)ca - (int)cb;
}

char *open_cfw_gx8002_stage2_strchr(const char *s, int c)
{
    unsigned char target = (unsigned char)c;
    for (;;) {
        unsigned char ch = (unsigned char)*s;
        if (ch == target) {
            return (char *)s;
        }
        if (ch == 0) {
            return NULL;
        }
        s++;
    }
}

size_t open_cfw_gx8002_stage2_strlen(const char *s)
{
    const char *p = s;
    while (*p != 0) {
        p++;
    }
    return (size_t)(p - s);
}

size_t open_cfw_gx8002_stage2_strnlen(const char *s, size_t maxlen)
{
    size_t n = 0;
    while (n < maxlen && s[n] != 0) {
        n++;
    }
    return n;
}
