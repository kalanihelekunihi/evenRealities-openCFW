#define _GNU_SOURCE
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern bool opencfw_em9305_packet_switch_known(uint8_t, uintptr_t, uintptr_t,
                                                 uint32_t, uint32_t *);
static unsigned pack6_calls,pack8_calls,mask_calls;
uint64_t opencfw_em9305_controller_pack_address(uintptr_t address)
{
    ++pack6_calls;
    uint64_t bits=0u;
    for(unsigned i=0;i<6;++i) bits|=(uint64_t)*(volatile uint8_t *)(address+i)<<(8u*i);
    return bits;
}
uint64_t opencfw_em9305_ll_pack64_304648(uintptr_t address)
{
    ++pack8_calls;
    uint64_t bits=0u;
    for(unsigned i=0;i<8;++i) bits|=(uint64_t)*(volatile uint8_t *)(address+i)<<(8u*i);
    return bits;
}
uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t low,uint32_t high)
{ (void)low; (void)high; ++mask_calls; return 2u; }

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) ==
           (void *)0x800000u);
    const uint8_t opcode[]={0u,1u,9u,12u,15u,20u,22u,24u,28u,31u,32u,33u,42u};
    const uint8_t state[]={12u,8u,9u,6u,24u,9u,3u,5u,35u,36u,9u,16u,43u};
    unsigned cases=0;
    for(unsigned index=0;index<sizeof opcode;++index) {
        memset((void *)0x800000u,0,0x100000u);
        uint8_t *f=(uint8_t *)0x80000cu,*p=(uint8_t *)0x801000u;
        for(unsigned i=1;i<=50;++i) p[i]=(uint8_t)(i*7u+3u);
        if(opcode[index]==1u) p[5]=1u;
        *(volatile uint8_t *)0x800005u=state[index];
        *(volatile uint32_t *)0x805a94u=0xffffffffu;
        *(volatile uint8_t *)0x805a95u=0xffu;
        *(volatile uint8_t *)0x805a97u=0xffu;
        pack6_calls=pack8_calls=mask_calls=0u;
        uint32_t result=0xffffffffu;
        assert(opencfw_em9305_packet_switch_known(opcode[index],0x800000u,
                                                   0x801000u,opcode[index]==32u?0u:1u,&result));
        assert(result!=25u);
        if(opcode[index]==9u) {
            assert(pack8_calls==1u);
            for(unsigned i=0;i<8;++i) assert(f[i]==p[i+1]);
        }
        if(opcode[index]==28u||opcode[index]==42u) {
            assert(pack6_calls==1u);
            for(unsigned i=0;i<24;++i) assert(f[i]==p[i+1]);
        }
        if(opcode[index]==20u) {
            for(unsigned i=0;i<8;++i) assert(f[i]==p[i+1]);
        }
        if(opcode[index]==1u) assert(mask_calls==1u);
        ++cases;
    }
    printf("PASS connected packet real-child routes %u host fixtures\n",cases);
    return 0;
}
