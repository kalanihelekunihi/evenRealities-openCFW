#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_packet_child_32dffc(uint32_t, uintptr_t, uint32_t);
extern uint32_t opencfw_em9305_packet_child_32e068(uint32_t, uintptr_t, uint32_t);
static uintptr_t observed_pack;
uint64_t opencfw_em9305_controller_pack_address(uintptr_t address)
{
    observed_pack=address;
    uint64_t bits=0u;
    for(unsigned i=0;i<6;++i) bits|=(uint64_t)*(volatile uint8_t *)(address+i)<<(8u*i);
    return bits;
}

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) ==
           (void *)0x800000u);
    uint8_t *f=(uint8_t *)0x80000cu,*p=(uint8_t *)0x801000u;
    unsigned cases=0;
    for(unsigned seed=0;seed<256;++seed)
    for(unsigned ext=0;ext<2;++ext) {
        memset(f,0xcc,56);
        for(unsigned i=1;i<=42;++i) p[i]=(uint8_t)(seed+i*37u);
        uint32_t result=ext?
            opencfw_em9305_packet_child_32e068(0x80000cu,0x801000u,0xa5u):
            opencfw_em9305_packet_child_32dffc(0x80000cu,0x801000u,0xa5u);
        assert(result==(ext?43u:35u));
        assert(observed_pack==0x80101bu);
        for(unsigned i=0;i<24;++i) assert(f[i]==p[i+1]);
        assert(f[24]==(p[25]&15u));
        assert(f[25]==((p[25]>>4)&1u));
        assert(f[26]==(p[25]>>5));
        assert(f[27]==p[26]);
        for(unsigned i=0;i<6;++i) assert(f[28+i]==p[27+i]);
        assert(f[34]==0u&&f[35]==0u);
        assert(f[36]==p[33]&&f[37]==p[34]);
        if(ext) {
            for(unsigned i=0;i<8;++i) assert(f[40+i]==p[35+i]);
            assert(f[48]==0xcc);
        } else assert(f[40]==0xcc);
        ++cases;
    }
    printf("PASS packet long children %u source/contract fixtures\n",cases);
    return 0;
}
