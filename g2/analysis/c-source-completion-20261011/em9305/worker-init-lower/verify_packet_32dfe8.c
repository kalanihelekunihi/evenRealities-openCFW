#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_packet_child_32dfe8(uint32_t, uintptr_t, uint32_t);
static uintptr_t observed_input;
uint64_t opencfw_em9305_ll_pack64_304648(uintptr_t input)
{
    observed_input=input;
    uint64_t bits=0u;
    for(unsigned i=0;i<8;++i) bits|=(uint64_t)*(volatile uint8_t *)(input+i)<<(8u*i);
    return bits;
}

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) ==
           (void *)0x800000u);
    uint8_t *f=(uint8_t *)0x80000cu,*p=(uint8_t *)0x801000u;
    unsigned cases=0;
    for(unsigned seed=0;seed<256;++seed) {
        memset(f,0xcc,16);
        for(unsigned i=1;i<=8;++i) p[i]=(uint8_t)(seed+i*37u);
        assert(opencfw_em9305_packet_child_32dfe8(0x80000cu,0x801000u,0xa5u)==9u);
        assert(observed_input==0x801001u);
        for(unsigned i=0;i<8;++i) assert(f[i]==p[i+1]);
        assert(f[8]==0xcc);
        ++cases;
    }
    printf("PASS packet 32dfe8 %u source/contract fixtures\n",cases);
    return 0;
}
