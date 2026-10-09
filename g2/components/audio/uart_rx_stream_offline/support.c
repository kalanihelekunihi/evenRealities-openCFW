/* Bounded offline support. Byte loops reconstructed for non-overlapping SRAM
 * memcpy/memset calls, independently compared through original providers.
 * BASEPRI operations reuse the already explained main port contract. */
#include "compat.h"
void *offline_copy(void *d,const void *s,size_t n){uint8_t *p=d;const uint8_t *q=s;for(size_t i=0;i<n;i++)p[i]=q[i];return d;}
void *offline_fill(void *d,int v,size_t n){uint8_t *p=d;for(size_t i=0;i<n;i++)p[i]=(uint8_t)v;return d;}
UBaseType_t offline_mask_set(void){uint32_t old;const uint32_t threshold=0x30;__asm volatile("mrs %0,basepri\nmsr basepri,%1\ndsb\nisb":"=&r"(old):"r"(threshold):"memory");return old;}
void offline_mask_restore(UBaseType_t old){__asm volatile("msr basepri,%0"::"r"(old):"memory");}
