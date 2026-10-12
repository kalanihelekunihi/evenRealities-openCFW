#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_secondary_commit_321e14(uint32_t);
extern const uint16_t opencfw_em9305_init_secondary_intervals_3357d0[8];
static unsigned stage,insert_count,seed_count,active_case,time_count;
static uint32_t third_time,last_time;
static uint8_t *const record=(uint8_t *)(uintptr_t)0x807000u;
static uint8_t *const slots=(uint8_t *)(uintptr_t)0x806000u;
#define U8(p) (*(uint8_t *)(uintptr_t)(p))
#define U16(p) (*(uint16_t *)(uintptr_t)(p))
#define U32(p) (*(uint32_t *)(uintptr_t)(p))
static void map_page(uintptr_t a)
{
    void *p=mmap((void *)a,4096u,PROT_READ|PROT_WRITE,
        MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p==(void *)a);
}
uint32_t opencfw_em9305_init_secondary_channel_324c68(uintptr_t p)
{
    assert(stage==0u&&p==(uintptr_t)(record+644u));
    assert(U32(record+620u)==120u&&U32(record+644u)==0x101u);
    stage=1u;return (uint32_t)p;
}
uint32_t opencfw_em9305_init_secondary_schedule_318ad8(uintptr_t p,uint32_t current)
{
    assert(p==(uintptr_t)slots);
    if(stage==1u){assert(current==U16(0x8051c0u+6u));stage=2u;return 1000u;}
    assert(stage==2u&&current==U16(slots+262u));stage=3u;return 2000u;
}
uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t a,uint32_t b)
{assert(stage==3u&&b==2000u&&(a!=0u));stage=4u;return 55u;}
uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t p,uint32_t seed)
{
    assert(p==(uintptr_t)(record+644u));
    assert(stage>=4u);
    seed_count++;
    return seed+0x40u;
}
uint32_t opencfw_em9305_init_secondary_current_303f5c(void)
{assert(seed_count==1u);return 40u;}
uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t a,uint32_t b)
{
    uint32_t result=a+b+1u;
    time_count++;last_time=result;
    if(time_count==3u){
        third_time=result;
        U8(0x805fbcu+2u)=0u; /* Fresh mode after third child call. */
        U16(record+248u)=321u; /* Fresh halfword copied twice. */
    }
    return result;
}
uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t p,uint32_t zero)
{
    assert(p==(uintptr_t)(record+48u)&&zero==0u);
    U32(record+60u)=99u;
    stage=5u;return 0u;
}
uintptr_t opencfw_em9305_init_secondary_compare_3249e8(uintptr_t a,uintptr_t b)
{return a^b;}
uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t p,uintptr_t compare)
{
    assert(stage==5u&&p==(uintptr_t)(record+48u));
    assert(compare==(uintptr_t)&opencfw_em9305_init_secondary_compare_3249e8);
    assert(U32(record+264u)==99u);
    insert_count++;
    if(insert_count==1u)U32(record+60u)=0xdeadu;
    return insert_count==1u?0u:0x77u;
}
static void setup(unsigned active,unsigned stress)
{
    memset((void *)0x805000u,0,4096u);
    memset((void *)0x806000u,0,4096u);
    memset((void *)0x807000u,0,4096u);
    memset((void *)0x808000u,0,4096u);
    active_case=active;
    stage=insert_count=seed_count=time_count=0u;
    third_time=last_time=0u;
    U32(0x805c70u)=0x806000u;
    U32(0x8051d0u)=0x807000u;
    U8(slots+614u)=3u;
    U16(slots+616u)=20u;
    U16(slots+618u)=12u;
    U16(slots+262u)=(uint16_t)(stress?0u:40u);
    U16(slots+266u)=(uint16_t)(stress?65535u:2u);
    U32(slots+28u)=100u;
    U8(0x805fbcu+16u)=2u;
    U8(0x805fbcu+3u)=1u;
    U8(0x805fbcu+2u)=1u;
    U32(0x805fbcu+8u)=0x101u;
    U32(0x805fbcu+12u)=0x202u;
    U32(0x805fbcu+20u)=0x303u;
    U32(0x805fbcu+24u)=0x404u;
    U16(0x805fbcu)=3u;
    U16(0x805fbcu+28u)=100u;
    U16(0x8051c0u+6u)=(uint16_t)(stress?32767u:50u);
    U16(0x8051c0u+8u)=(uint16_t)(stress?32766u:60u);
    U16(0x8051c0u+10u)=(uint16_t)(stress?0u:20u);
    U8(0x8051c0u+12u)=1u;
    U16(0x8051c0u+14u)=10u;
    U32(record+252u)=5u;
    U32(record+60u)=7u;
    U8(record+777u)=(uint8_t)active;
    U8(record+512u)=2u;
    U8(record+513u)=3u;
    U32(record+780u)=0x808000u;
}
int main(void)
{
    map_page(0x805000u);map_page(0x806000u);map_page(0x807000u);
    map_page(0x808000u);
    const uint16_t expected[8]={500u,250u,150u,100u,75u,50u,30u,20u};
    for(unsigned i=0u;i<8u;i++)
        assert(opencfw_em9305_init_secondary_intervals_3357d0[i]==expected[i]);
    for(unsigned scenario=0u;scenario<3u;scenario++){
        unsigned active=scenario==1u;
        setup(active,scenario==2u);
        assert(opencfw_em9305_init_secondary_commit_321e14(
            active==0u?0u:0x10000u)==0x77u);
        assert(stage==5u&&insert_count==2u&&seed_count==2u);
        assert(time_count==5u);
        assert(U16(record+278u)==321u&&U16(record+276u)==321u);
        assert(U32(record+268u)==30u+2u*(third_time+16u));
        assert(U32(record+60u)==99u+last_time+16u);
        assert(U8(record+97u)!=0u);
        assert(U16(record+248u)!=0u);
        assert(U8(record+777u)==active_case);
        for(unsigned i=0u;i<15u;i++)assert(U16(record+280u+2u*i)==0xfffu);
        assert(U16(record+310u)==0u);
    }
    return 0;
}
