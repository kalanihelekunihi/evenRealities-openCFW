/* Freestanding C library declarations for the recovered G2 nanopb build.
 * This is first-party build glue, not an upstream nanopb source edit.
 */
#ifndef OPENCFW_PB_G2_SYSTEM_H
#define OPENCFW_PB_G2_SYSTEM_H
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <limits.h>

void *memcpy(void *restrict, const void *restrict, size_t);
void *memset(void *, int, size_t);
size_t strlen(const char *);
#endif
