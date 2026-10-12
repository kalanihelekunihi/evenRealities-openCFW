#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_registered_3263ec(uintptr_t);
static uintptr_t const root=0x811000u,state=0x803ddcu,product=0x804080u,packet=0x812000u;
static unsigned alloc_calls,send_calls,accuracy_calls;
static uint32_t expected_alloc,alloc_fail;
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes)
{assert(bytes==expected_alloc);++alloc_calls;return alloc_fail?0u:(uint32_t)packet;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t source,uintptr_t buffer)
{assert(source==root&&buffer==packet);++send_calls;return 0x1234u;}
uint32_t opencfw_em9305_init_secondary_schedule_318ad8(uintptr_t source,uint32_t value)
{assert(source==root&&value==37u);return 1000u;}
uint32_t opencfw_em9305_auxiliary_guard_interval(void){return 50u;}
uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t current,uint32_t previous)
{uint32_t d=current-previous;return (d&0x80000000u)!=0u?0u:d;}
uint32_t opencfw_em9305_compose_accuracy_318988(void)
{++accuracy_calls;return 3u;}
uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t dest,uint32_t low,uint32_t high)
{assert(dest==packet+27u&&low==0x44332211u&&high==0x6655u);for(unsigned i=0;i<6u;++i)*(uint8_t *)(dest+i)=(uint8_t)(i+1u);return dest+6u;}
static void setup(void)
{
    memset((void *)root,0,4096u);memset((void *)0x803000u,0,0x3000u);
    memset((void *)packet,0xa5,4096u);
    *(uint16_t *)(root+612u)=0u;
    *(uint16_t *)(root+260u)=10u;
    *(uint16_t *)(root+262u)=20u;
    *(uint16_t *)(root+592u)=5u;
    *(uint8_t *)(root+610u)=0x11u;
    *(uint8_t *)(root+611u)=0x22u;
    *(uint32_t *)(state+172u)=100u;
    *(uint32_t *)(state+152u)=1000u;
    *(uint8_t *)(state+156u)=3u;
    *(uint16_t *)(state+176u)=3u;
    *(uint32_t *)(state+544u)=0x88776655u;
    *(uint32_t *)(state+548u)=2u;
    *(uint32_t *)(state+628u)=0x44332211u;
    *(uint32_t *)(state+632u)=0x6655u;
    *(uint8_t *)(state+616u)=1u;
    *(uint8_t *)(state+618u)=1u;
    *(uint8_t *)(state+676u)=2u;
    *(uint8_t *)(state+0u)=0x12u;
    *(uint8_t *)(state+1u)=0x34u;
    *(uint8_t *)(state+2u)=0x56u;
    *(uint8_t *)(state+3u)=0x78u;
    *(uint8_t *)(state+4u)=0x9au;
    *(uint8_t *)(state+5u)=0xbcu;
    *(uint8_t *)(state+6u)=0xdeu;
}
int main(void)
{
    assert(mmap((void *)0x803000u,0x3000u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x803000u);
    for(uintptr_t base=0x811000u;base<=0x812000u;base+=4096u)
        assert(mmap((void *)base,4096u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)base);
    setup();expected_alloc=35u;
    assert(opencfw_em9305_init_registered_3263ec(root)==0x1234u);
    assert(alloc_calls==1u&&send_calls==1u&&accuracy_calls==1u);
    assert(*(uint8_t *)(packet+0u)==0x1cu&&*(uint8_t *)(packet+1u)==0x11u&&*(uint8_t *)(packet+2u)==0x22u);
    assert(*(uint8_t *)(packet+3u)==3u&&*(uint8_t *)(packet+4u)==0u);
    assert(*(uint8_t *)(packet+7u)==0x55u&&*(uint8_t *)(packet+8u)==0x66u&&*(uint8_t *)(packet+9u)==0x77u&&*(uint8_t *)(packet+10u)==0x88u);
    assert(*(uint8_t *)(packet+11u)==0x62u&&*(uint8_t *)(packet+12u)==0x12u&&*(uint8_t *)(packet+18u)==0xdeu);
    assert(*(uint8_t *)(packet+19u)==4u&&*(uint8_t *)(packet+20u)==0u&&*(uint8_t *)(packet+21u)==37u);
    assert(*(uint8_t *)(packet+25u)==0x71u&&*(uint8_t *)(packet+26u)==2u);
    for(unsigned i=0;i<6u;++i)assert(*(uint8_t *)(packet+27u+i)==i+1u);
    assert(*(uint8_t *)(packet+35u)==0xa5u);
    setup();expected_alloc=43u;
    *(uint8_t *)(product+1u)=1u;
    *(uint32_t *)(product+4u)=0x805000u;
    *(uint8_t *)(0x805000u+18u)=0u;
    *(uint8_t *)(0x803f78u)=1u;
    for(unsigned i=0;i<8u;++i)*(uint8_t *)(state+408u+i)=(uint8_t)(0x80u+i);
    assert(opencfw_em9305_init_registered_3263ec(root)==0x1234u);
    assert(*(uint8_t *)packet==0x2au);
    for(unsigned i=0;i<8u;++i)assert(*(uint8_t *)(packet+35u+i)==0x80u+i);
    /* Host radix-4 model only: DIVU denominator zero retains its R1
     * destination, which native initialized to the state address. */
    setup();expected_alloc=35u;
    *(uint32_t *)(state+152u)=0u;
    assert(opencfw_em9305_init_registered_3263ec(root)==0x1234u);
    assert(*(uint8_t *)(packet+19u)==(uint8_t)(state+4u));
    assert(*(uint8_t *)(packet+20u)==(uint8_t)((state+4u)>>8u));
    setup();expected_alloc=35u;alloc_fail=1u;
    assert(opencfw_em9305_init_registered_3263ec(root)==0u);
    assert(*(uint8_t *)packet==0xa5u&&send_calls==3u);
    return 0;
}
