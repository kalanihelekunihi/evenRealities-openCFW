/* Arm EABI memory-call wrappers over attributable upstream C bodies.
 * Alignment suffixes permit aligned arguments; general C implementations also
 * accept them. These are source candidates, not original Arm runtime code. */
#include <stddef.h>
#include <string.h>
void __aeabi_memcpy4(void *dest,const void *src,size_t n) { (void)memcpy(dest,src,n); }
void __aeabi_memclr4(void *dest,size_t n) { (void)memset(dest,0,n); }
void __aeabi_memclr8(void *dest,size_t n) { (void)memset(dest,0,n); }
void __aeabi_memclr(void *dest,size_t n) { (void)memset(dest,0,n); }
