#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_event_322b70(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_313338(uintptr_t);
static unsigned callback_calls;
uint32_t opencfw_em9305_auxiliary_transition_333a60(void)
{ return 0x88776655u; }
static uint32_t callback(uintptr_t context,uint32_t zero)
{
    volatile uint8_t *p=(volatile uint8_t *)context;
    assert(zero==0u && p[321]==2u && p[76]==0x47u && p[77]==0x47u);
    ++callback_calls;
    return 0x123u;
}
int main(void)
{
    assert((uintptr_t)callback<=UINT32_MAX);
    assert(mmap((void *)0x800000u,0x10000u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void *)-1);
    uint8_t *ctx=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                      MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(ctx!=(void *)-1);
    uint8_t *cfg=mmap((void *)0x820000u,4096u,PROT_READ|PROT_WRITE,
                      MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(cfg!=(void *)-1);
    cfg[53]=2u;cfg[54]=0x47u;
    *(volatile uint32_t *)(uintptr_t)0x805c6cu=0x820000u;
    *(volatile uint32_t *)(uintptr_t)(0x8027e0u+8u)=(uint32_t)(uintptr_t)callback;
    *(volatile uint32_t *)(uintptr_t)0x805f14u=0x810010u;
    *(volatile uint8_t *)(uintptr_t)0x805f04u=2u;
    assert(opencfw_em9305_mode_event_322b70((uintptr_t)ctx)==2u);
    assert(callback_calls==1u && ctx[65]==0x23u);
    return 0;
}
