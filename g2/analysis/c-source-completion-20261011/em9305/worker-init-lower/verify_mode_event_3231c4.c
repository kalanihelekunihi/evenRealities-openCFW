#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_event_3231c4(uintptr_t);
static unsigned event_calls,accept_calls,copy_calls;
static uint8_t snapshot[10];
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event)
{
    volatile uint8_t *p=(volatile uint8_t *)event;
    for(unsigned i=0;i<9u;i++) snapshot[i]=p[i];
    ++event_calls;
    return 0xabcdu;
}
void *opencfw_em9305_memcpy(void *destination,const void *source,uint32_t bytes)
{
    ++copy_calls;
    return memcpy(destination,source,bytes);
}
static uint32_t accept(uint32_t index,uintptr_t self)
{
    ++accept_calls;
    assert(index==0u && self==(uintptr_t)accept);
    return 1u;
}
int main(void)
{
    assert(mmap((void *)0x800000u,0x10000u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)-1);
    uint8_t *ctx=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(ctx!=(void *)-1);
    *(volatile uint32_t *)(uintptr_t)0x805c70u=0x810000u;
    ctx[12]=255u;
    assert(opencfw_em9305_mode_event_3231c4((uintptr_t)ctx)==0x810000u);
    assert(event_calls==0u && copy_calls==0u);
    ctx[12]=42u;
    assert(opencfw_em9305_mode_event_3231c4((uintptr_t)ctx)==0xabcdu);
    assert(event_calls==1u && snapshot[0]==0u && snapshot[2]==6u);
    assert(snapshot[4]==0u && snapshot[6]==0u && snapshot[8]==42u);
    *(volatile uint32_t *)(uintptr_t)0x8028c4u=(uint32_t)(uintptr_t)accept;
    assert((uintptr_t)accept<=UINT32_MAX);
    ctx[636]=1u;
    assert(opencfw_em9305_mode_event_3231c4((uintptr_t)ctx)==0x810320u);
    assert(accept_calls==1u && copy_calls==1u && event_calls==1u);
    assert(ctx[798]==1u && ctx[800]==0u && ctx[802]==6u);
    assert(ctx[804]==0u && ctx[806]==0u && ctx[808]==22u);
    return 0;
}
