#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
#include <stdbool.h>
extern bool goodix_primitives_byte_fill(uint8_t,uint8_t *,size_t);
/* Canonical firmware pool cell. The portable goodix_heap context has a
 * different interface and is not an alias for this native descriptor. */
uint8_t *volatile r1_goodix_native_heap_pool
    __attribute__((section(".r1.goodix.native.heap.pool"),aligned(4)));
_Static_assert(sizeof(uintptr_t)==4,"native allocator pointer words");
int32_t r1_goodix_native_pool_initialize(void *pool,uint32_t size)
{
    if (!pool) return -1;
    if (size-1024u>=UINT32_C(0x3ffffc01)) return -2;
    uintptr_t base=(uintptr_t)pool;
    volatile uint32_t *words=(volatile uint32_t *)pool;
    r1_goodix_native_heap_pool=pool;
    words[0]=0;
    for (uint32_t i=0;i<2;i++) {
        uintptr_t anchor=base+4u+i*8u;
        *(volatile uint32_t *)(anchor+8u)=(uint32_t)anchor;
        *(volatile uint32_t *)(anchor+12u)=(uint32_t)anchor;
    }
    uintptr_t top=(base+0x33u)&~(uintptr_t)7u;
    uintptr_t end=base+size;
    words[8]=(uint32_t)top;
    words[9]=(uint32_t)end;
    uint32_t available=(uint32_t)(end-top-16u);
    words[7]=(uint32_t)top;
    words[10]=available;
    *(volatile uint32_t *)(top+4u)=available<<2;
    return 0;
}
int32_t goodix_mem_init(void *pool,int32_t size)
{
    if (!pool) return -1;
    if (size<=0) return -2;
    (void)goodix_primitives_byte_fill(0,pool,(size_t)size);
    return r1_goodix_native_pool_initialize(pool,(uint32_t)size);
}
