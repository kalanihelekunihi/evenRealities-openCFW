#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_packet_child_32dc40(uint32_t, uintptr_t, uint32_t);

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) ==
           (void *)0x800000u);
    uint8_t *f=(uint8_t *)0x80000cu,*p=(uint8_t *)0x801000u;
    unsigned cases=0;
    for(unsigned seed=0;seed<256;++seed) {
        memset(f,0xcc,64);
        for(unsigned i=1;i<=35;++i) p[i]=(uint8_t)(seed+i*37u);
        assert(opencfw_em9305_packet_child_32dc40(0x80000cu,0x801000u,0xa5u)==36u);
        for(unsigned i=0;i<4;++i) assert(f[i]==p[i+1]);
        assert(f[4]==((p[6]>>7)&1u) && f[5]==0xcc);
        assert(*(uint16_t *)(f+6)==((((uint16_t)p[5]|((uint16_t)p[6]<<8)))&0xfffu));
        assert(*(uint16_t *)(f+8)==((((uint16_t)p[7]|((uint16_t)p[8]<<8)))&0xfffu));
        assert(*(uint32_t *)(f+12)==(((uint32_t)p[9]|((uint32_t)p[10]<<8)|((uint32_t)p[11]<<16))&0xfffffu));
        assert(*(uint32_t *)(f+16)==(((uint32_t)p[12]|((uint32_t)p[13]<<8)|((uint32_t)p[14]<<16))&0xfffffu));
        assert(f[20]==p[15]&&f[21]==p[16]&&f[22]==p[17]&&f[23]==p[18]);
        assert(f[24]==p[19]&&f[25]==0xcc&&f[26]==0xcc&&f[27]==0xcc);
        assert(f[28]==p[20]&&f[29]==p[21]&&f[30]==p[22]&&f[31]==0u);
        assert(f[32]==(p[23]&15u)&&f[33]==(p[23]>>4));
        assert(f[34]==p[24]&&f[35]==p[25]);
        assert(f[36]==p[26]&&f[37]==p[27]);
        assert(f[40]==p[28]&&f[41]==p[29]&&f[42]==p[30]&&f[43]==0u);
        assert(f[44]==p[31]&&f[45]==p[32]&&f[46]==p[33]&&f[47]==0u);
        assert(f[48]==p[34]&&f[49]==p[35]&&f[50]==0xcc);
        ++cases;
    }
    printf("PASS packet 32dc40 %u source/contract fixtures\n",cases);
    return 0;
}
