#ifndef G2_CORDIO_STRING_H
#define G2_CORDIO_STRING_H
/* Minimal freestanding declarations needed to compile the pinned Cordio
 * utility source with the installed clang cross target. */
void *memcpy(void *destination, const void *source, __SIZE_TYPE__ size);
void *memset(void *destination, int value, __SIZE_TYPE__ size);
int memcmp(const void *left, const void *right, __SIZE_TYPE__ size);
#endif
