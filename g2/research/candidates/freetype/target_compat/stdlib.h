/* SPDX-License-Identifier: FTL */
/* Declaration-only bare-target boundary; see ../README.md. */
#ifndef OPEN_CFW_FREETYPE_TARGET_STDLIB_H
#define OPEN_CFW_FREETYPE_TARGET_STDLIB_H
#include <stddef.h>
void *calloc(size_t count, size_t size);
void free(void *block);
void *malloc(size_t size);
void *realloc(void *block, size_t size);
void qsort(
    void *base,
    size_t count,
    size_t size,
    int (*compare)(const void *, const void *)
);
long strtol(const char *text, char **end, int base);
char *getenv(const char *name);
#endif
