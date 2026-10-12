#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_packet_child_32dba4(uint32_t, uintptr_t, uint32_t);

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) ==
           (void *)0x800000u);
    uint8_t *fields=(uint8_t *)0x80000cu;
    uint8_t *packet=(uint8_t *)0x801000u;
    unsigned cases=0;
    for(unsigned seed=0;seed<256;++seed) {
        memset(fields,0xcc,16);
        for(unsigned i=1;i<=7;++i) packet[i]=(uint8_t)(seed+i*31u);
        assert(opencfw_em9305_packet_child_32dba4(0x80000cu,0x801000u,0xa5u)==8u);
        for(unsigned i=0;i<4;++i) assert(fields[i]==packet[i+1]);
        assert(fields[4]==packet[5]);
        assert(fields[5]==0u && fields[6]==0u && fields[7]==0u);
        assert(fields[8]==packet[6] && fields[9]==packet[7] && fields[10]==0xcc);
        ++cases;
    }
    printf("PASS packet accumulator child %u source/contract fixtures\n",cases);
    return 0;
}
