#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
extern void *memset(void *,int,size_t);
#include "native_graph_initialize.h"
extern void *r1_goodix_native_graph_mode6_create(const void *,const uint32_t *);
static uint32_t word(uintptr_t p) { return *(const volatile uint32_t *)p; }
static void put(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }
void *r1_goodix_native_graph_mode0_create(const void *weights,const uint32_t *parameters)
{
    void *allocation=goodix_mem_malloc(732);
    if (!allocation) return NULL;
    (void)memset(allocation,0,732);
    uintptr_t p=(uintptr_t)allocation;
    put(p,0);r1_goodix_native_graph_initialize(allocation,weights);
    put(p+0x238,word(p+0x1e0));
    uintptr_t params=(uintptr_t)parameters;
    uintptr_t remap=word(params+4);
    if (remap) {
        uint32_t code=word(params),groups=word(remap);
        /* Native UDIV produces zero for a zero divisor; no loop then runs. */
        uint32_t stride=groups ? ((code>>2)-1u)/groups : 0;
        for (uint32_t i=0;i<groups;i++) {
            uintptr_t entry=remap+((i*stride)<<2);
            uint32_t target=word(entry+4);
            put(p+0x238+(target<<2),(uint32_t)(entry+8));
        }
    }
    return allocation;
}
void *r1_goodix_native_graph_mode1_create(const void *weights,const uint32_t *parameters)
{
    (void)parameters;
    void *allocation=goodix_mem_malloc(568);
    if (!allocation) return NULL;
    put((uintptr_t)allocation,1);
    r1_goodix_native_graph_initialize(allocation,weights);
    return allocation;
}
void *r1_goodix_native_graph_mode2_create(const void *weights,const uint32_t *parameters)
{
    (void)parameters;
    void *allocation=goodix_mem_malloc(572);
    if (!allocation) return NULL;
    put((uintptr_t)allocation,2);
    r1_goodix_native_graph_initialize(allocation,weights);
    return allocation;
}
void *r1_goodix_native_graph_record_create(uint32_t *record)
{
    uintptr_t p=(uintptr_t)record;
    if (!word(p+4)) return NULL;
    typedef void *(*constructor)(const void *,const uint32_t *);
    static const constructor providers[7]={
        r1_goodix_native_graph_mode0_create,
        r1_goodix_native_graph_mode1_create,
        r1_goodix_native_graph_mode2_create,
        NULL,NULL,NULL,
        r1_goodix_native_graph_mode6_create
    };
    /* Nonnull weights require a native selector0,1,2 or6. */
    uint32_t selector=word(p);
    return providers[selector]((const void *)(uintptr_t)word(p+4),(const uint32_t *)(p+8));
}
