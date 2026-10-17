/* C11 declarations for compiling pinned Cordio source freestanding.
 * Implementations are supplied by the selected firmware runtime.
 */
#ifndef G2_VENDOR_COMPAT_STRING_H
#define G2_VENDOR_COMPAT_STRING_H
#include <stddef.h>
void *memcpy(void *restrict destination,const void *restrict source,size_t count);
void *memset(void *destination,int value,size_t count);
int memcmp(const void *left,const void *right,size_t count);
#endif
