/* SPDX-License-Identifier: MIT
 * Genuine freestanding compiler support for the isolated GNU CASE profile.
 * Standard nonoverlapping byte-copy/fill semantics; no native-address or
 * body-coverage claim. Compile without builtin loop-to-call substitution.
 */
#include <stddef.h>
void *memcpy(void *destination,const void *source,size_t size)
{
 unsigned char *out=destination;const unsigned char *in=source;
 for(size_t i=0;i<size;i++)out[i]=in[i];
 return destination;
}
void *memset(void *destination,int value,size_t size)
{
 unsigned char *out=destination;
 for(size_t i=0;i<size;i++)out[i]=(unsigned char)value;
 return destination;
}
