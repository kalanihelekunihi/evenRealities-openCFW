#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_transition_prepare_31a700(
    uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
static const uintptr_t request=0x810000u;
static const uintptr_t nested0=0x820000u;
static const uintptr_t nested1=0x821000u;
static const uintptr_t nested2=0x822000u;
static const uintptr_t connection=0x830000u;
static const uintptr_t base=0x82f550u;
static unsigned scenario,stage;

uintptr_t opencfw_em9305_init_connection_allocate_316c58(void)
{ assert(stage==0);stage=1;return scenario==0u?0u:connection; }
uint32_t opencfw_em9305_associated_slot_allocate_3133b4(
    uint32_t id,uint32_t direction,uint32_t minimum,uint32_t maximum,
    uint32_t extent,uintptr_t output,uintptr_t callback)
{
    assert(stage==1);stage=2;
    assert(id==3u&&direction==0u&&minimum==2500u&&maximum==3750u);
    assert(extent==77u&&callback!=0u);
    if(scenario==1u)return 0u;
    *(uint32_t *)output=500u;
    /* Native R18 retains nested0; R13 must reload this slot after child. */
    *(uint32_t *)(request+0xafcu)=(uint32_t)nested1;
    return 1u;
}
uint32_t opencfw_em9305_init_connection_query_31b21c(uint32_t id,uintptr_t out)
{(void)id;(void)out;assert(0);return 0u;}
uint32_t opencfw_em9305_radio_access_raw_318878(void)
{assert(stage==2);stage=3;return 0x1234u;}
uint32_t opencfw_em9305_radio_crc_seed_318960(void)
{
    assert(stage==3&&*(uint32_t *)(nested1+116u)==0x1234u);
    /* CRC changes the slot: later 96 read is fresh, subsequent stores use
     * the captured R13 object. */
    *(uint32_t *)(request+0xafcu)=(uint32_t)nested2;
    stage=4;return 0x5566u;
}
uint32_t opencfw_em9305_associated_random_31896c(void)
{assert(stage==4&&*(uint16_t *)(nested1+132u)==0x2468u);stage=5;return 0x92u;}
uint32_t opencfw_em9305_compose_accuracy_318988(void)
{
    assert(stage==5&&*(uint8_t *)(nested1+142u)==0x92u);
    /* Accuracy changes the slot again: target ID and mode use fresh R3,
     * whereas byte143 remains on captured R13. */
    *(uint32_t *)(request+0xafcu)=(uint32_t)nested0;
    stage=6;return 0x47u;
}
uint32_t opencfw_em9305_common_request_30455c(uint32_t id)
{assert(stage==6&&id==1u&&*(uint8_t *)(base+3u*912u+524u)==0x26u);stage=7;return 0u;}
uint32_t opencfw_em9305_command_count_30e4bc(void)
{assert(stage==7&&*(uint8_t *)(uintptr_t)0x805a74u==5u);stage=8;return 0u;}
uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t c)
{assert(stage==2&&c==connection);stage=3;return 0u;}
uint32_t opencfw_em9305_init_transition_report_316908(
    uint32_t id,uint32_t status,uint32_t fresh,uint32_t low,uint32_t high)
{
    assert((scenario==0u&&stage==1&&status==9u)||
           (scenario==1u&&stage==3&&status==13u));
    assert(id==0x23u&&fresh==0x26u&&low==0x12345678u&&high==0x9abcdef0u);
    stage=4;return 0u;
}
uint32_t opencfw_em9305_init_transition_finish_325eb4(uintptr_t req,uint32_t reason)
{assert(stage==4&&req==request&&reason==2u);stage=5;return 0u;}
static void write16(uintptr_t address,uint16_t value)
{*(uint16_t *)address=value;}
static void write32(uintptr_t address,uint32_t value)
{*(uint32_t *)address=value;}
static void reset_fixture(void)
{
    memset((void *)(uintptr_t)0x800000u,0,0x100000u);
    stage=0u;
    write32(request+0xafcu,(uint32_t)nested0);
    *(uint8_t *)(request+1u)=0x23u;
    write32(request+16u,0x11112222u);
    write32(request+20u,0x33334444u);
    write16(nested0+82u,2u);
    write16(nested0+84u,3u);
    write16(nested0+86u,0x56u);
    write16(nested0+88u,0x78u);
    write16(connection+592u,77u);
    write32((uintptr_t)0x805c70u,(uint32_t)base);
    write32(nested1+68u,0xaaaabbbbu);
    write32(nested1+72u,0xccccddddu);
    write16(nested2+96u,0x2468u);
    write16(nested0+94u,3u);
    write32((uintptr_t)0x805aa0u,0x11223344u);
    write32((uintptr_t)0x805aa4u,0x55667788u);
    *(uint8_t *)(uintptr_t)0x805a74u=4u;
}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    for(scenario=0u;scenario<3u;scenario++) {
        reset_fixture();
        uint32_t result=opencfw_em9305_init_transition_prepare_31a700(
            request,0x26u,0x12345678u,0x9abcdef0u,0x44u,0x37u);
        if(scenario==0u)assert(result==9u&&stage==5u);
        if(scenario==1u)assert(result==13u&&stage==5u);
        if(scenario==2u) {
            assert(result==0u&&stage==8u);
            assert(*(uint32_t *)(nested1+100u)==0x11112222u);
            assert(*(uint32_t *)(nested1+104u)==0x33334444u);
            assert(*(uint16_t *)(nested1+136u)==0x78u);
            assert(*(uint16_t *)(nested1+134u)==0x56u);
            assert(*(uint16_t *)(nested1+132u)==0x2468u);
            assert(*(uint8_t *)(nested0+65u)==0x37u);
            assert(*(uint8_t *)(nested1+143u)==0x47u);
            assert(*(uint8_t *)(nested2+143u)==0u);
            assert(*(uint32_t *)(base+3u*912u+516u)==0x12345678u);
            assert(*(uint32_t *)(base+3u*912u+520u)==0x9abcdef0u);
        }
    }
    return 0;
}
