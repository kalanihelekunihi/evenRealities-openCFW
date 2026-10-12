#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_packet_child_32dd20(uint32_t, uintptr_t, uint32_t);
extern uint32_t opencfw_em9305_packet_child_32dbe4(uint32_t, uintptr_t, uint32_t);

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) ==
           (void *)0x800000u);
    uint8_t *fields=(uint8_t *)0x80000cu;
    uint8_t *packet=(uint8_t *)0x801000u;
    unsigned cases=0;
    for (unsigned seed=0;seed<256;++seed) {
        for(unsigned i=0;i<20;++i) packet[i]=(uint8_t)(seed+i*23u);
        memset(fields,0xcc,24);
        assert(opencfw_em9305_packet_child_32dd20(0x80000cu,0x801000u,0xa5u)==9u);
        for(unsigned i=0;i<3;++i) assert(fields[i]==packet[i+1]);
        assert(fields[3]==0u);
        for(unsigned i=0;i<3;++i) assert(fields[i+4]==packet[i+4]);
        assert(fields[7]==0u && fields[8]==packet[7] && fields[9]==packet[8]);
        assert(fields[10]==0xcc);
        ++cases;
        memset(fields,0xcc,24);
        assert(opencfw_em9305_packet_child_32dbe4(0x80000cu,0x801000u,0xa5u)==16u);
        for(unsigned i=0;i<4;++i) assert(fields[i]==packet[i+1]);
        for(unsigned group=1;group<4;++group) {
            for(unsigned i=0;i<3;++i) assert(fields[group*4+i]==packet[group*3+i+2]);
            assert(fields[group*4+3]==0u);
        }
        assert(fields[16]==packet[14] && fields[17]==packet[15] && fields[18]==0xcc);
        ++cases;
    }
    printf("PASS packet word children %u source/contract fixtures\n",cases);
    return 0;
}
