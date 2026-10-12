#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_init_registered_32613c(uintptr_t);
static uintptr_t const root=0x811000u,record=0x810000u,packet=0x812000u;
static unsigned alloc_calls,send_calls,accuracy_calls;
static uint32_t expected_alloc,alloc_fail;
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id)
{assert(id==7u);return record;}
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
{
    assert(dest==packet+27u&&low==0x44332211u&&high==0x6655u);
    for(unsigned i=0;i<6u;++i)*(uint8_t *)(dest+i)=(uint8_t)(i+1u);
    return dest+6u;
}
static void setup(void)
{
    memset((void *)root,0,4096u);memset((void *)record,0,4096u);
    memset((void *)packet,0xa5,4096u);
    *(uint8_t *)(root+612u)=7u;
    *(uint16_t *)(root+260u)=10u;
    *(uint16_t *)(root+262u)=20u;
    *(uint16_t *)(root+592u)=5u;
    *(uint8_t *)(root+610u)=0x11u;
    *(uint8_t *)(root+611u)=0x22u;
    *(uint32_t *)(record+388u)=100u;
    *(uint32_t *)(record+700u)=1000u;
    *(uint16_t *)(record+376u)=3u;
    *(uint32_t *)(record+720u)=0x88776655u;
    *(uint32_t *)(record+724u)=2u;
    *(uint32_t *)(record+16u)=0x44332211u;
    *(uint32_t *)(record+20u)=0x6655u;
    *(uint8_t *)(record+66u)=1u;
    *(uint8_t *)(record+440u)=2u;
    *(uint8_t *)(record+432u)=0x12u;
    *(uint8_t *)(record+433u)=0x34u;
    *(uint8_t *)(record+434u)=0x56u;
    *(uint8_t *)(record+435u)=0x78u;
    *(uint8_t *)(record+436u)=0x9au;
    *(uint8_t *)(record+437u)=0xbcu;
    *(uint8_t *)(record+438u)=0xdeu;
    *(uint8_t *)(record+439u)=0xf0u;
}
int main(void)
{
    for(uintptr_t base=0x810000u;base<=0x812000u;base+=4096u)
        assert(mmap((void *)base,4096u,PROT_READ|PROT_WRITE,
                    MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)base);
    setup();expected_alloc=35u;
    assert(opencfw_em9305_init_registered_32613c(root)==0x1234u);
    assert(alloc_calls==1u&&send_calls==1u&&accuracy_calls==2u);
    assert(*(uint8_t *)(packet+0u)==0x1cu);
    assert(*(uint8_t *)(packet+1u)==0x11u);
    assert(*(uint8_t *)(packet+2u)==0x22u);
    assert(*(uint8_t *)(packet+3u)==3u);
    assert(*(uint8_t *)(packet+4u)==0u);
    assert(*(uint8_t *)(packet+7u)==0x55u);
    assert(*(uint8_t *)(packet+8u)==0x66u);
    assert(*(uint8_t *)(packet+9u)==0x77u);
    assert(*(uint8_t *)(packet+10u)==0x88u);
    assert(*(uint8_t *)(packet+11u)==0x62u);
    assert(*(uint8_t *)(packet+12u)==0x12u&&*(uint8_t *)(packet+18u)==0xdeu);
    assert(*(uint8_t *)(packet+19u)==4u&&*(uint8_t *)(packet+20u)==0u);
    assert(*(uint8_t *)(packet+21u)==37u&&*(uint8_t *)(packet+22u)==0u);
    assert(*(uint8_t *)(packet+25u)==0x61u);
    assert(*(uint8_t *)(packet+26u)==2u);
    for(unsigned i=0;i<6u;++i)assert(*(uint8_t *)(packet+27u+i)==i+1u);
    assert(*(uint8_t *)(packet+33u)==20u);
    assert(*(uint8_t *)(packet+34u)==0u);
    assert(*(uint8_t *)(packet+35u)==0xa5u);
    setup();expected_alloc=43u;
    *(uint8_t *)(record+2809u)=1u;
    for(unsigned i=0;i<8u;++i)*(uint8_t *)(record+784u+i)=(uint8_t)(0x80u+i);
    *(uint8_t *)(record+796u)=0x9au;
    *(uint8_t *)(record+797u)=0xbcu;
    assert(opencfw_em9305_init_registered_32613c(root)==0x1234u);
    assert(*(uint8_t *)packet==0x2au);
    for(unsigned i=0;i<6u;++i)
        assert(*(uint8_t *)(packet+35u+i)==0x80u+i);
    assert(*(uint8_t *)(packet+41u)==0x9au);
    assert(*(uint8_t *)(packet+42u)==0xbcu);
    setup();expected_alloc=35u;alloc_fail=1u;
    assert(opencfw_em9305_init_registered_32613c(root)==0u);
    assert(*(uint8_t *)packet==0xa5u && send_calls==2u);
    return 0;
}
