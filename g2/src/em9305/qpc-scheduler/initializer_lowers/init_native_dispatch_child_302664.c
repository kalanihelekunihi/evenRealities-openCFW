#include <stdint.h>

/* Native 0x302664..0x3026a8: overlap-aware byte copy (memmove). An
 * overlapping forward move copies backwards; otherwise 9 or more bytes
 * go through memcpy and shorter runs are copied bytewise. Returns dst. */
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);

uintptr_t opencfw_em9305_dispatch_child_302664(uintptr_t destination,
                                               uintptr_t source,uint32_t bytes)
{
    if(source<destination&&destination<source+bytes){
        volatile uint8_t *to=(volatile uint8_t *)(destination+bytes);
        const volatile uint8_t *from=(const volatile uint8_t *)(source+bytes);
        while(bytes!=0u){
            *--to=*--from;
            --bytes;
        }
        return destination;
    }
    if(bytes>=9u){
        (void)opencfw_em9305_memcpy((void *)destination,(const void *)source,bytes);
        return destination;
    }
    volatile uint8_t *to=(volatile uint8_t *)destination;
    const volatile uint8_t *from=(const volatile uint8_t *)source;
    for(;bytes!=0u;--bytes)*to++=*from++;
    return destination;
}
