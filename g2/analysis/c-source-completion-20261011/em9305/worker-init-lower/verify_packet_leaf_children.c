#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_packet_child_32de6c(uint32_t, uintptr_t, uint32_t);
extern uint32_t opencfw_em9305_packet_child_32deac(uint32_t, uintptr_t, uint32_t);
extern uint32_t opencfw_em9305_packet_child_32e1f4(uint32_t, uintptr_t, uint32_t);

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) ==
           (void *)0x800000u);
    unsigned cases = 0;
    for (unsigned seed = 0; seed < 256; ++seed) {
        uint8_t *fields = (uint8_t *)0x80000cu;
        uint8_t *payload = (uint8_t *)0x801000u;
        for (unsigned i = 0; i < 32; ++i)
            payload[i] = (uint8_t)(seed + i * 37u);
        memset(fields, 0xcc, 32);
        assert(opencfw_em9305_packet_child_32de6c(0x80000cu, 0x801000u, 0xa5u) == 12u);
        assert(fields[0] == payload[1] && fields[1] == 0xcc);
        for (unsigned i = 2; i < 12; ++i) assert(fields[i] == payload[i]);
        ++cases;
        memset(fields, 0xcc, 32);
        assert(opencfw_em9305_packet_child_32deac(0x80000cu, 0x801000u, 0xa5u) == 9u);
        for (unsigned i = 0; i < 8; ++i) assert(fields[i] == payload[i + 1]);
        assert(fields[8] == 0xcc);
        ++cases;
        memset(fields, 0xcc, 32);
        assert(opencfw_em9305_packet_child_32e1f4(0x80000cu, 0x801000u, 0xa5u) == 6u);
        assert(fields[0] == payload[1] && fields[1] == 0xcc);
        for (unsigned i = 2; i < 6; ++i) assert(fields[i] == payload[i]);
        assert(fields[6] == 0xcc);
        ++cases;
    }
    printf("PASS packet leaf children %u source/contract fixtures\n", cases);
    return 0;
}
