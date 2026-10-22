/* SPDX-License-Identifier: MIT
 * Freestanding <stdlib.h> for pinned upstream units in the G2 Apollo main
 * image. strtod is the IAR DLIB entry at 0x542D48 (cJSON parse_number
 * receives its result in d0: hard-float calling convention).
 */
#ifndef G2_UPSTREAM_LIBC_STDLIB_H
#define G2_UPSTREAM_LIBC_STDLIB_H
#include <stddef.h>
void *malloc(size_t size);
void *calloc(size_t count, size_t size);
void *realloc(void *pointer, size_t size);
void free(void *pointer);
double strtod(const char *string, char **end);
long strtol(const char *string, char **end, int base);
unsigned long strtoul(const char *string, char **end, int base);
int abs(int value);
#endif
