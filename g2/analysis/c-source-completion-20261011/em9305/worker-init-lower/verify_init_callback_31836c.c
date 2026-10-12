#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_init_callback_child_303918(uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_init_callback_31836c(uintptr_t,uintptr_t,uintptr_t);
static uintptr_t found_row;
static unsigned pair_calls,private_calls,lookup_calls;
static uint32_t pair_return;
uintptr_t opencfw_em9305_radio_identity_find_31441c(uint32_t kind,uint32_t low,uint32_t high)
{assert(kind==1u&&low==0x1234u&&high==0x10000u);++lookup_calls;return found_row;}
uint64_t opencfw_em9305_radio_private_address_31467c(uintptr_t row)
{assert(row==found_row);++private_calls;return UINT64_C(0x5566778811223344);}
uint32_t opencfw_em9305_radio_identity_pair_303a60(uint32_t kind,uint32_t low,uint32_t high,uintptr_t output)
{assert(kind==1u&&low==0x1234u&&high==0x10000u);++pair_calls;
 if(pair_return!=0u){*(volatile uint32_t *)output=0x11u;*(volatile uint32_t *)(output+4u)=0x22u;}
 return pair_return;}
int main(void)
{
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *ctx=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                      MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *settings=mmap((void *)0x811000u,4096u,PROT_READ|PROT_WRITE,
                           MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *third=mmap((void *)0x812000u,4096u,PROT_READ|PROT_WRITE,
                        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *row=mmap((void *)0x813000u,4096u,PROT_READ|PROT_WRITE,
                      MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(root!=(void *)-1&&ctx!=(void *)-1&&settings!=(void *)-1&&third!=(void *)-1&&row!=(void *)-1);
    *(uint32_t *)(third+748u)=0x1234u;
    *(uint32_t *)(third+752u)=0x10000u;
    *(uint32_t *)(settings+80u)=0x5u;
    assert(opencfw_em9305_init_callback_31836c((uintptr_t)ctx,(uintptr_t)settings,(uintptr_t)third)==1u);
    assert(ctx[3]==1u&&pair_calls==0u&&*(uint32_t *)(settings+80u)==5u);
    root[0xa9du]=1u;root[0xafdu]=0u;
    assert(opencfw_em9305_init_callback_31836c((uintptr_t)ctx,(uintptr_t)settings,(uintptr_t)third)==0x45u);
    assert(pair_calls==0u&&*(uint32_t *)(settings+80u)==0x45u);
    root[0xafdu]=2u;pair_return=1u;
    assert(opencfw_em9305_init_callback_31836c((uintptr_t)ctx,(uintptr_t)settings,(uintptr_t)third)==0x45u);
    assert(pair_calls==1u&&lookup_calls==0u&&ctx[3]==1u);
    pair_return=0u;found_row=(uintptr_t)row;
    assert(opencfw_em9305_init_callback_31836c((uintptr_t)ctx,(uintptr_t)settings,(uintptr_t)third)==0x45u);
    assert(pair_calls==2u&&lookup_calls==1u&&private_calls==1u);
    assert(*(uint32_t *)(row+40u)==0x11223344u&&*(uint32_t *)(row+44u)==0x55667788u&&row[66]==1u);
    found_row=0u;
    uint32_t pair[2]={9u,9u};
    assert(opencfw_em9305_init_callback_child_303918(1u,0x1234u,0x10000u,(uintptr_t)pair)==0u);
    assert(pair[0]==9u&&pair[1]==9u);
    return 0;
}
