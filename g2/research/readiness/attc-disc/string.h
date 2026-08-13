#ifndef OPENCFW_ATTC_DISC_PROBE_STRING_H
#define OPENCFW_ATTC_DISC_PROBE_STRING_H

#include <stddef.h>

int memcmp(const void *a, const void *b, size_t n);
void *memcpy(void *restrict dst, const void *restrict src, size_t n);
void *memset(void *dst, int value, size_t n);

#endif
