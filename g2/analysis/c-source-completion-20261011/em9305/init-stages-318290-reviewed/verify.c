#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_transition_stage_318290(
    uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
uint32_t opencfw_em9305_init_transition_stage_318348(
    uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
static unsigned child_calls;
static uint32_t child_found;
uint32_t opencfw_em9305_radio_peer_pair_303a40(
    uint32_t kind,uint32_t low,uint32_t high,uintptr_t output)
{
    assert(kind==0x11u&&low==0x22u&&high==0x33u);
    ++child_calls;
    if(child_found){*(uint32_t *)output=0x1234u;
        *(uint32_t *)(output+4u)=0x5678u;}
    return child_found;
}
uint32_t opencfw_em9305_init_callback_child_303918(
    uint32_t kind,uint32_t low,uint32_t high,uintptr_t output)
{
    assert(kind==0x11u&&low==0x22u&&high==0x33u);
    assert(output==0x804000u);
    ++child_calls;
    return 0xfeedu;
}
static uint32_t rd(uintptr_t p){return *(uint32_t *)p;}
static void run(unsigned kind,unsigned special,unsigned found)
{
    memset((void *)(uintptr_t)0x800000u,0,0x70000u);
    child_calls=0u;child_found=found;
    *(uint32_t *)(uintptr_t)0x805b40u=0x1111u;
    *(uint32_t *)(uintptr_t)0x805b44u=0x2222u;
    *(uint32_t *)(uintptr_t)0x805a8cu=0x3333u;
    *(uint32_t *)(uintptr_t)0x805a90u=0x4444u;
    *(uint8_t *)(uintptr_t)0x805a81u=(uint8_t)special;
    *(uint32_t *)(uintptr_t)0x802050u=0x40u;
    uint32_t result=opencfw_em9305_init_transition_stage_318290(
        0x802000u,0x803000u,kind,0x11u,0x22u,0x33u,0x804000u);
    assert(child_calls==((kind&2u)!=0u?1u:0u));
    if((kind&2u)==0u||!found)
        assert(*(uint8_t *)(uintptr_t)0x805be2u==(uint8_t)(kind&~2u));
    uint32_t low=(kind&2u)&&found?0x1234u:
        ((kind&~2u)==1u&&special?0x3333u:0x1111u);
    uint32_t high=(kind&2u)&&found?0x5678u:
        ((kind&~2u)==1u&&special?0x4444u:0x2222u);
    assert(rd(0x804000u)==low&&rd(0x804004u)==high);
    assert(rd(0x802054u)==low&&rd(0x802058u)==high);
    assert(rd(0x80205cu)==0x22u&&rd(0x802060u)==0x33u);
    assert(result==rd(0x802050u));
    assert((result&1u)!=0u&&(result&8u)!=0u);
    assert(((result&2u)!=0u)==((((kind&2u)!=0u)&&found)||
        ((kind&~2u)==1u&&special)));
    if((kind&2u)&&found){assert(rd(0x805be4u)==0x1234u);
        assert(rd(0x805be8u)==0x5678u);}
    assert(*(uint8_t *)(uintptr_t)0x803002u==
        (uint8_t)((((kind&2u)&&found)||((kind&~2u)==1u&&special))?1u:0u));
}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x70000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    for(unsigned kind=0;kind<4;kind++)
        for(unsigned special=0;special<2;special++)
            for(unsigned found=0;found<2;found++)run(kind,special,found);
    memset(p,0,0x70000u);child_calls=0u;
    *(uint32_t *)(uintptr_t)0x802050u=0xffu;
    *(uint8_t *)(uintptr_t)0x805a9du=1u;
    assert(opencfw_em9305_init_transition_stage_318348(
        0x802000u,0u,0x11u,0x22u,0x33u,0x804000u)==0xffu);
    assert(child_calls==1u&&rd(0x802050u)==0xffu);
    *(uint8_t *)(uintptr_t)0x805a9du=0u;
    assert(opencfw_em9305_init_transition_stage_318348(
        0x802000u,0u,0x11u,0x22u,0x33u,0x804000u)==0xbfu);
    return 0;
}
