#ifndef G2_FT_ANALYSIS_STDLIB_H
#define G2_FT_ANALYSIS_STDLIB_H
#include <stddef.h>
void qsort(void *, size_t, size_t, int (*)(const void *, const void *));
void *calloc(size_t, size_t);
void free(void *);
void *malloc(size_t);
void *realloc(void *, size_t);
long strtol(const char *, char **, int);
char *getenv(const char *);
#endif
