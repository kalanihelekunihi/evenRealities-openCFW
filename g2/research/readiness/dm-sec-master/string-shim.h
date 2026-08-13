#ifndef OPENCFW_PROBE_STRING_H
#define OPENCFW_PROBE_STRING_H
#include <stddef.h>
void *memcpy(void *restrict dst, const void *restrict src, size_t n);
void *memset(void *dst, int c, size_t n);
int memcmp(const void *lhs, const void *rhs, size_t n);
#endif
