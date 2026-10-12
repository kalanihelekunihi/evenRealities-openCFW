#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_callback_3183ec(uintptr_t,uintptr_t);
static unsigned calls;
static uint32_t found;
uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t kind,uint32_t low,
    uint32_t high,uintptr_t output)
{
    assert(kind==7u&&low==0x11223344u&&high==0x55667788u);
    ++calls;
    if (found!=0u) {
        *(volatile uint32_t *)output=0x1234u;
        *(volatile uint32_t *)(output+4u)=0x5678u;
    }
    return found;
}
int main(void)
{
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *ctx=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                      MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *record=mmap((void *)0x811000u,4096u,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(root!=(void *)-1&&ctx!=(void *)-1&&record!=(void *)-1);
    *(uint32_t *)(record+152u)=0x11223344u;
    *(uint32_t *)(record+156u)=0x55667788u;
    record[163u]=7u;
    root[0xafdu]=0u;
    assert(opencfw_em9305_init_callback_3183ec((uintptr_t)ctx,(uintptr_t)record)==0x810000u);
    assert(ctx[2]==0u&&calls==0u);
    root[0xafdu]=1u;root[0xa81u]=1u;
    assert(opencfw_em9305_init_callback_3183ec((uintptr_t)ctx,(uintptr_t)record)==0x805a70u);
    assert(ctx[2]==1u&&root[0xa80u]==0u&&calls==0u);
    root[0xafdu]=3u;found=0u;
    assert(opencfw_em9305_init_callback_3183ec((uintptr_t)ctx,(uintptr_t)record)==0u);
    assert(ctx[2]==0u&&calls==1u);
    found=1u;
    assert(opencfw_em9305_init_callback_3183ec((uintptr_t)ctx,(uintptr_t)record)==0x1234u);
    assert(ctx[2]==1u&&calls==2u);
    assert(*(uint32_t *)(root+0xb04u)==0x1234u&&*(uint32_t *)(root+0xb08u)==0x5678u);
    return 0;
}
