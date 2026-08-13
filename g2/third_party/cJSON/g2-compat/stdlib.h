#ifndef G2_COMPAT_STDLIB_H
#define G2_COMPAT_STDLIB_H
#include <stddef.h>
void *malloc(size_t size);
void *realloc(void *ptr, size_t size);
void free(void *ptr);
double strtod(const char *nptr, char **endptr);
#endif
