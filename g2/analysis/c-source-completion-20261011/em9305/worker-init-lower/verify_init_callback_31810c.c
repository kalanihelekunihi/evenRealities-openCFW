#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_callback_31810c(uint32_t);
static uintptr_t slot0,slot1;
static unsigned calls;
void *opencfw_em9305_memset(void *destination,uint32_t value,uint32_t bytes)
{
    assert(value==0u);
    if (calls==0u) {
        assert((uintptr_t)destination==0x820064u&&bytes==44u);
        *(volatile uint32_t *)slot0=0x820100u;
    } else if (calls==1u)
        assert((uintptr_t)destination==0x820152u&&bytes==12u);
    else if (calls==2u)
        assert((uintptr_t)destination==0x821064u&&bytes==44u);
    else if (calls==3u)
        assert((uintptr_t)destination==0x821052u&&bytes==12u);
    else assert(0);
    ++calls;return memset(destination,0,bytes);
}
int main(void)
{
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *base=mmap((void *)0x810000u,8192u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *objects=mmap((void *)0x820000u,8192u,PROT_READ|PROT_WRITE,
                          MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(root!=(void *)-1&&base!=(void *)-1&&objects!=(void *)-1);
    assert(opencfw_em9305_init_callback_31810c(0u)==1u&&calls==0u);
    *(uint32_t *)(root+0xc38u)=0x810000u;
    slot0=(uintptr_t)(base+0xafcu);
    slot1=(uintptr_t)(base+0xb08u+0xafcu);
    *(uint32_t *)slot0=0x820000u;*(uint32_t *)slot1=0x821000u;
    *(uint32_t *)(objects+96u)=0xffffffffu;
    *(uint32_t *)(objects+0x1000u+96u)=0xffffffffu;
    memset(objects+100u,0xa5,44u);
    memset(objects+0x1000u+100u,0xa5,44u);
    assert(opencfw_em9305_init_callback_31810c(0x55u)==1u);
    assert(calls==4u);
    assert(*(uint16_t *)(objects+96u)==0u&&*(uint16_t *)(objects+94u)==0u);
    assert(objects[80]==0u&&*(uint16_t *)(objects+76u)==0u);
    assert(*(uint16_t *)(objects+0x1000u+96u)==0u);
    for(unsigned i=0;i<44u;i++) assert(objects[100u+i]==0u);
    for(unsigned i=0;i<12u;i++) assert(objects[0x1000u+82u+i]==0u);
    return 0;
}
