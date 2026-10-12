#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_packet_child_32de08(uint32_t, uintptr_t, uint32_t);

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) ==
           (void *)0x800000u);
    uint8_t *f=(uint8_t *)0x80000cu,*p=(uint8_t *)0x801000u;
    unsigned cases=0;
    for(unsigned seed=0;seed<256;++seed) {
        memset(f,0xcc,32);
        for(unsigned i=1;i<=23;++i) p[i]=(uint8_t)(seed+i*37u);
        assert(opencfw_em9305_packet_child_32de08(0x80000cu,0x801000u,0xa5u)==24u);
        for(unsigned i=0;i<8;++i) assert(f[i]==p[i+1]);
        assert(f[8]==p[9]&&f[9]==0xcc);
        for(unsigned i=10;i<24;++i) assert(f[i]==p[i]);
        assert(f[24]==0xcc);
        ++cases;
    }
    printf("PASS packet 32de08 %u source/contract fixtures\n",cases);
    return 0;
}
