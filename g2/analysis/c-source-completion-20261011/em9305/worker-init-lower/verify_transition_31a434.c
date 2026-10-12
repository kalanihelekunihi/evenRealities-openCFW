#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
uint32_t opencfw_em9305_init_transition_31a434(uintptr_t);
static uintptr_t request=0x810000u,first=0x820000u,second=0x821000u;
static uintptr_t base=0x830000u,connection=0x830000u+2u*912u;
static uintptr_t event=0x840000u;
static unsigned scenario,calls;
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes)
{assert(bytes==88u&&calls==0u);calls=1u;return scenario?event:0u;}
void *opencfw_em9305_memcpy(void *dst,const void *src,uint32_t bytes)
{assert(calls==1u&&bytes==44u&&(uintptr_t)dst==event+4u&&
        (uintptr_t)src==first+100u);
 assert(*(uint8_t *)(connection+2u)==0u);
 calls=2u;*(uint32_t *)(request+0xafcu)=(uint32_t)second;
 return memcpy(dst,src,bytes);}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t message)
{assert(calls==2u&&handler==0x29u&&message==event);
 assert(*(uint16_t *)(event+2u)==0x3f01u);
 assert(*(uint8_t *)(event+52u)==1u);
 assert(*(uint8_t *)(event+53u)==0x51u);
 assert(*(uint8_t *)(event+54u)==0x52u);
 assert(*(uint8_t *)(event+84u)==0x53u);
 assert(*(uint32_t *)(event+60u)==0x12345678u);
 assert(*(uint32_t *)(event+64u)==0x4000u);
 calls=3u;return 0u;}
uint32_t opencfw_em9305_associated_schedule_insert_312da4(
    uintptr_t object,uintptr_t compare)
{assert(object==connection+16u&&compare!=0u);
 if(scenario==0u){assert(calls>=1u&&calls<=3u);calls++;return calls==4u;}
 assert(calls>=3u&&calls<=5u);calls++;return calls==6u;}
uint32_t opencfw_em9305_init_schedule_compare_318b78(uintptr_t a,uintptr_t b)
{(void)a;(void)b;assert(0);return 0u;}
uint32_t opencfw_em9305_init_transition_count_down_320068(void)
{assert(calls==(scenario?6u:4u));calls=7u;return 0xa5a5u;}
static void setup(void)
{
    memset((void *)(uintptr_t)0x800000u,0,0x100000u);
    calls=0u;
    *(uint32_t *)(request+0xafcu)=(uint32_t)first;
    *(uint16_t *)(first+94u)=2u;
    *(uint16_t *)(second+94u)=2u;
    *(uint32_t *)(uintptr_t)0x805c70u=(uint32_t)base;
    *(uint32_t *)(connection+24u)=100u;
    *(uint16_t *)(connection+266u)=2u;
    *(uint16_t *)(connection+262u)=7u;
    *(uint16_t *)(connection+532u)=9u; /* Reject mistaken word scaling. */
    *(uint16_t *)(connection+524u)=11u;
    *(uint8_t *)(request+2261u)=0x51u;
    *(uint8_t *)(request+63u)=0x52u;
    *(uint8_t *)(request+1u)=0x53u;
    *(uint32_t *)(second+112u)=0x4000u;
    *(uint32_t *)(second+108u)=0x12345678u;
    *(uint32_t *)(uintptr_t)0x805be4u=0x33445566u;
    *(uint32_t *)(uintptr_t)0x805be8u=0x778899aau;
    *(uint8_t *)(uintptr_t)0x805b18u=0x29u;
}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    for(scenario=0u;scenario<2u;scenario++){
        setup();
        assert(opencfw_em9305_init_transition_31a434(request)==0xa5a5u);
        assert(calls==7u);
        assert(*(uint16_t *)(connection+262u)==9u);
        assert(*(uint16_t *)(connection+524u)==11u);
        assert(*(uint32_t *)(connection+24u)==5100u);
    }
    return 0;
}
