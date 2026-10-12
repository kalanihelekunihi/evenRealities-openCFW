#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_packet_child_32e114(uint32_t, uintptr_t, uint32_t);
extern uint32_t opencfw_em9305_packet_child_32e128(uint32_t, uintptr_t, uint32_t);

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0) ==
           (void *)0x800000u);
    uint8_t *fields = (uint8_t *)0x80000cu;
    uint8_t *payload = (uint8_t *)0x801000u;
    unsigned cases = 0;
    for (unsigned first = 0; first < 256; ++first)
    for (unsigned second = 0; second < 256; ++second) {
        fields[0] = fields[1] = 0xffu;
        payload[1] = (uint8_t)first;
        payload[2] = (uint8_t)second;
        assert(opencfw_em9305_packet_child_32e114(0x80000cu,0x801000u,0xabu)==3u);
        assert(fields[0] == (first & 7u) && fields[1] == (second & 7u));
        ++cases;
    }
    for (unsigned seed = 0; seed < 256; ++seed) {
        for (unsigned i = 1; i <= 4; ++i) payload[i] = (uint8_t)(seed + i * 23u);
        fields[0] = fields[1] = fields[2] = fields[3] = fields[4] = 0xffu;
        assert(opencfw_em9305_packet_child_32e128(0x80000cu,0x801000u,0xabu)==5u);
        for (unsigned i = 0; i < 4; ++i) assert(fields[i] == payload[i + 1]);
        assert(fields[4] == 0xffu);
        ++cases;
    }
    printf("PASS packet mask children %u source/contract fixtures\n", cases);
    return 0;
}
