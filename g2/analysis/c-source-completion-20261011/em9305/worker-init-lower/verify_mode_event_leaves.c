#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_event_32c978(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32cadc(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_32279c(uintptr_t);
extern uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t);
static unsigned calls;
static uintptr_t arg0;
static uint32_t arg1;
uint32_t opencfw_em9305_mode_event_313338(uintptr_t field)
{++calls;arg0=field;return 0x313338u;}
uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t context,uint32_t byte12)
{
    assert(*(volatile uint32_t *)(context+636u)==0x21u);
    assert(*(volatile uint32_t *)(context+640u)==0u);
    ++calls;arg0=context;arg1=byte12;return 0x322fdcu;
}
int main(void)
{
    assert(mmap((void *)0x800000u,0x100000u,PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
    unsigned cases=0;
    for(unsigned byte=0;byte<256;++byte) {
        memset((void *)0x800000u,0,0x100000u);
        uintptr_t c=0x800100u;
        *(volatile uint8_t *)(c+12u)=(uint8_t)byte;
        assert(opencfw_em9305_mode_event_32c978(c)==c);
        assert(*(volatile uint8_t *)(c+12u)==0x3eu);
        assert(opencfw_em9305_mode_event_32cadc(c)==c);
        assert(*(volatile uint8_t *)(c+12u)==0x22u);
        calls=0u;
        assert(opencfw_em9305_mode_event_32279c(c)==0x313338u);
        assert(calls==1u&&arg0==c+16u);
        *(volatile uint32_t *)(c+636u)=0x21u;
        calls=0u;
        assert(opencfw_em9305_mode_event_31ac3c(c)==c);
        assert(calls==0u);
        *(volatile uint8_t *)(c+12u)=(uint8_t)byte;
        *(volatile uint32_t *)(c+636u)=0x20021u;
        *(volatile uint32_t *)(c+640u)=0xffffffffu;
        assert(opencfw_em9305_mode_event_31ac3c(c)==0x322fdcu);
        assert(calls==1u&&arg0==c&&arg1==byte);
        ++cases;
    }
    printf("PASS mode/event leaves %u source/contract fixtures\n",cases);
    return 0;
}
