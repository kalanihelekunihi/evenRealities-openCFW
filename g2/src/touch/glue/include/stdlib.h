/* SPDX-License-Identifier: MIT — freestanding stand-in for PDL */
#ifndef G2_TOUCH_STDLIB_H
#define G2_TOUCH_STDLIB_H
#include <stddef.h>
void *malloc(size_t n);
void free(void *p);
void *calloc(size_t n, size_t sz);
void abort(void);
int abs(int x);
long labs(long x);
#endif
