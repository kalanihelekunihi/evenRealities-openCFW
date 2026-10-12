#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_event_313338(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32cb40(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32cf78(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t,uint32_t);
static unsigned transitioned,callbacks;
static uint8_t observed[16];
uint32_t opencfw_em9305_auxiliary_transition_333a60(void)
{ ++transitioned; return 0x33445566u; }
uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event)
{
    volatile uint8_t *p=(volatile uint8_t *)event;
    for (unsigned i=0;i<14u;i++) observed[i]=p[i];
    ++callbacks;
    return 0x778899aau;
}
static uint16_t h(const uint8_t *p,unsigned at)
{ return (uint16_t)(p[at]|((uint16_t)p[at+1u]<<8u)); }
static uint32_t w(const uint8_t *p,unsigned at)
{ return (uint32_t)p[at]|((uint32_t)p[at+1u]<<8u)|((uint32_t)p[at+2u]<<16u)|((uint32_t)p[at+3u]<<24u); }
int main(void)
{
    uint8_t *p=mmap((void *)0x804000u,0x20000u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    *(volatile uint32_t *)(uintptr_t)0x805f14u=0x806000u;
    *(volatile uint8_t *)(uintptr_t)0x805f04u=1u;
    assert(opencfw_em9305_mode_event_313338(0x807000u)==0x807000u);
    assert(transitioned==0u);
    assert(opencfw_em9305_mode_event_313338(0x806000u)==0x33445566u);
    assert(transitioned==1u);
    *(volatile uint8_t *)(uintptr_t)0x805f04u=2u;
    assert(opencfw_em9305_mode_event_313338(0x806000u)==2u);
    assert(transitioned==1u);
    uint8_t *ctx=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                      MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(ctx!=(void *)-1);
    assert(opencfw_em9305_mode_event_32cb40((uintptr_t)ctx)==0x810000u);
    assert(ctx[12]==0x3du);
    assert(opencfw_em9305_mode_event_32cf78((uintptr_t)ctx)==0x810000u);
    assert(ctx[12]==0xffu);
    *(volatile uint32_t *)(uintptr_t)0x805c70u=0x810000u;
    *(volatile uint32_t *)(ctx+676u)=0xa1b2c3d4u;
    *(volatile uint16_t *)(ctx+680u)=0x1234u;
    assert(opencfw_em9305_mode_event_322fdc((uintptr_t)ctx,0u)==0x778899aau);
    assert(callbacks==1u && h(observed,0u)==0u && observed[2]==7u);
    assert(observed[3]==0u && observed[4]==0u && h(observed,6u)==0u);
    assert(w(observed,8u)==0xa1b2c3d4u && h(observed,12u)==0x1234u);
    assert(opencfw_em9305_mode_event_322fdc((uintptr_t)ctx+912u,0x22u)==0x778899aau);
    assert(callbacks==2u && h(observed,0u)==1u && observed[2]==7u);
    assert(observed[3]==0x22u && observed[4]==0x22u && h(observed,6u)==1u);
    assert(w(observed,8u)==0u && h(observed,12u)==0u);
    return 0;
}
