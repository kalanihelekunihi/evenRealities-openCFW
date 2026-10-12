#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_packet_entry_319204(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_packet_entry_3191ac(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_packet_entry_3191c4(uint32_t,uint32_t,uint32_t);
static uint32_t child_calls, child_arg;
uint32_t opencfw_em9305_child_32e1f4(uint32_t fields)
{ ++child_calls; child_arg=fields; return 0xabcdef01u; }

int main(void)
{
    assert(mmap((void *)0x800000u, 0x2000u, PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
    *(volatile uint8_t *)0x801001u=0x42u;
    for (unsigned state=0;state<8;++state) {
        *(volatile uint8_t *)0x800005u=(uint8_t)state;
        *(volatile uint8_t *)0x80000cu=0u;
        *(volatile uint8_t *)0x80000du=0u;
        assert(opencfw_em9305_packet_entry_319204(0x800000u,0x801000u,3u)==25u);
        assert(opencfw_em9305_packet_entry_3191ac(0x800000u,0x801000u,3u)==(state==2u?0u:25u));
        assert(*(volatile uint8_t *)0x80000cu==255u && *(volatile uint8_t *)0x80000du==0x42u);
        child_calls=0u;
        assert(opencfw_em9305_packet_entry_3191c4(0x800000u,0x801000u,3u)==(state==6u?0u:25u));
        assert(child_calls==1u && child_arg==0x80000cu);
    }
    puts("PASS packet entries 319204/3191ac/3191c4 eight states");
    return 0;
}
