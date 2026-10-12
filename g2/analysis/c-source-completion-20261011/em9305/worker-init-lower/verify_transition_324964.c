#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_init_transition_324964(uintptr_t);
static uintptr_t record;
static unsigned calls;
uint32_t opencfw_em9305_init_secondary_fill_324768(uintptr_t r,uint8_t *response)
{assert(r==record&&calls==0u);calls=1u;for(unsigned i=0;i<18;i++)response[i]=(uint8_t)i;
 *(uint8_t *)(record+777u)=0x56u;return 0u;}
uint32_t opencfw_em9305_init_secondary_event_30e928(
    uint32_t kind,uint32_t id,uint8_t *response,uint32_t feature)
{assert(calls==1u&&kind==0u&&id==2u&&feature==0x56u);
 for(unsigned i=0;i<18;i++)assert(response[i]==i);
 calls=2u;return 0x1234u;}
uint32_t opencfw_em9305_init_transition_event_308664(
    uint32_t kind,uintptr_t r,uint32_t feature)
{assert(calls==0u&&kind==0u&&r==record&&feature==0x44u);
 calls=3u;return 0xabcd;
}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    record=0x803d78u+784u*2u;
    *(uint8_t *)(record+9u)=7u;
    assert(opencfw_em9305_init_transition_324964(record)==7u&&calls==0u);
    *(uint8_t *)(record+9u)=12u;
    *(uint8_t *)(record+777u)=0x44u;
    assert(opencfw_em9305_init_transition_324964(record)==0xabcdu&&calls==3u);
    calls=0u;
    *(uint8_t *)(record+9u)=11u;
    assert(opencfw_em9305_init_transition_324964(record)==0x1234u&&calls==2u);
    return 0;
}
