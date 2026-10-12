#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_transition_secondary_32d138_body(uint8_t *);
static const uintptr_t message=0x810000u,record=0x820000u,target=0x830000u;
static unsigned scenario,stage;
uint32_t opencfw_em9305_init_secondary_allocate_316e74(void)
{ assert(stage==0u);stage=1u;return scenario==2u?0u:(uint32_t)record; }
uint32_t opencfw_em9305_common_request_30455c(uint32_t value)
{ assert(stage==1u&&value==1u);stage=2u;return 0u; }
uint32_t opencfw_em9305_radio_secondary_encode_32e164(uintptr_t out,uintptr_t src)
{
    assert(stage==2u&&out==0x805fbcu&&src==message+6u);
    assert(*(uint8_t *)(record+625u)==0x25u);
    stage=3u;*(uint8_t *)(out+4u)=0x9au;return 0u;
}
uint32_t opencfw_em9305_radio_resolve_303bdc(
    uint32_t low,uint32_t high,uintptr_t kind,uintptr_t output)
{
    assert(scenario==1u&&stage==3u);
    assert(low==0x12345678u&&high==0x4000u);
    assert(*(uint8_t *)kind==0u);
    assert(*(uint32_t *)output==0u&&*(uint32_t *)(output+4u)==0u);
    *(uint8_t *)kind=0x21u;
    *(uint32_t *)output=0x55667788u;
    *(uint32_t *)(output+4u)=0x99aabbccu;
    stage=4u;return 1u;
}
uint32_t opencfw_em9305_init_secondary_start_3213f8(uintptr_t current)
{
    assert(stage==(scenario==1u?4u:3u));
    assert(current==record);
    assert(*(uint8_t *)(record+515u)==0x84u);
    assert(*(uint32_t *)(record+252u)==192500u);
    if(scenario==1u) {
        assert(*(uint32_t *)(record+720u)==0x55667788u);
        assert(*(uint32_t *)(record+724u)==0x99aabbccu);
        assert(*(uint8_t *)(record+717u)==0x23u);
    }
    stage=5u;return 0u;
}
uint32_t opencfw_em9305_command_count_30e4bc(void)
{ assert(stage==5u);stage=6u;return 0u; }
uint32_t opencfw_em9305_init_secondary_commit_321e14(uint32_t a)
{
    assert(stage==6u);
    assert(a==0x1111u);
    assert(*(uint16_t *)(uintptr_t)0x8051c2u==0x1111u);
    assert(*(uint16_t *)(uintptr_t)0x8051c4u==0x2222u);
    assert(*(uint32_t *)(uintptr_t)0x8051d4u==0x33334444u);
    assert(*(uint8_t *)(uintptr_t)0x8051dbu==0x84u);
    stage=7u;return 0x5aa5u;
}
uint32_t opencfw_em9305_init_secondary_finish_321820(void)
{ assert(stage==7u);stage=8u;return 0xa55a55a5u; }
static void setup(void)
{
    memset((void *)(uintptr_t)0x800000u,0,0x100000u);
    stage=0u;
    *(uint32_t *)(uintptr_t)0x805c80u=(uint32_t)message;
    *(uint32_t *)(record+92u)=(uint32_t)target;
    *(uint16_t *)(uintptr_t)0x805fc0u=3u;
    *(uint8_t *)(message+32u)=0x25u;
    *(uint8_t *)(message+33u)=(uint8_t)(scenario==1u?1u:0u);
    *(uint8_t *)(message+35u)=0x35u;
    *(uint32_t *)(message+36u)=0x12345678u;
    *(uint32_t *)(message+40u)=0x4000u;
    *(uint32_t *)(message+48u)=0x33334444u;
    *(uint16_t *)(message+24u)=0x1111u;
    *(uint16_t *)(message+4u)=0x2222u;
    *(uint8_t *)(message+52u)=0x81u;
    *(uint8_t *)(message+53u)=0x82u;
    *(uint8_t *)(message+54u)=0x83u;
    *(uint8_t *)(message+55u)=0x84u;
}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    for(scenario=0u;scenario<3u;scenario++) {
        setup();
        uint8_t frame[12] __attribute__((aligned(4)));
        memset(frame,0xa5,sizeof frame);
        uint32_t result=opencfw_em9305_init_transition_secondary_32d138_body(frame);
        if(scenario==2u)assert(result==0u&&stage==1u);
        else {
            assert(result==0xa55a55a5u&&stage==8u);
            assert(*(uint8_t *)(uintptr_t)0x805fc0u==0x9au);
            assert(*(uint32_t *)(record+76u)==0u);
            assert(*(uint32_t *)(target+72u)==0u);
        }
        assert(frame[8]==0xa5u&&frame[9]==0xa5u&&frame[10]==0xa5u);
    }
    return 0;
}
