#include <assert.h>
#include <stdint.h>
#include <string.h>

uint32_t opencfw_em9305_init_transition_record_3239b8(
    uintptr_t,uint32_t,uint32_t,uintptr_t);
uint32_t opencfw_em9305_init_transition_segment_3243dc(
    uintptr_t,uint32_t,uint32_t,uintptr_t);
uint32_t opencfw_em9305_init_transition_record_323c78(
    uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t);
static unsigned writes,copies;
static uintptr_t mutating_record;
uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t output,uint32_t low,uint32_t high)
{
    uint8_t *p=(uint8_t *)output;
    assert(low==(writes==0u?0x11223344u:0x99aabbccu));
    assert(high==(writes==0u?0x55667788u:0xddeeff00u));
    for(unsigned i=0;i<6u;i++)p[i]=(uint8_t)(writes*16u+i);
    writes++;
    if(mutating_record!=0u)*(uint8_t *)(mutating_record+31u)=3u;
    return output+6u;
}
void *opencfw_em9305_memcpy(void *dest,const void *src,uint32_t n)
{assert(n==3u);copies++;return memcpy(dest,src,n);}
int main(void)
{
    uint8_t record[40]={0},out[40]={0};
    for(unsigned i=0;i<40u;i++)record[i]=(uint8_t)(0x40u+i);
    record[31]=9u;
    mutating_record=(uintptr_t)record;
    assert(opencfw_em9305_init_transition_record_3239b8((uintptr_t)out,
        0x11223344u,0x55667788u,(uintptr_t)record)==15u);
    assert(writes==1u&&copies==1u&&memcmp(out+6u,record,3u)==0);
    memset(out,0,sizeof out);record[31]=1u;writes=0u;copies=0u;
    assert(opencfw_em9305_init_transition_segment_3243dc((uintptr_t)out,
        0x11223344u,0x55667788u,(uintptr_t)record)==7u);
    assert(writes==1u&&copies==1u);
    mutating_record=0u;writes=0u;
    assert(opencfw_em9305_init_transition_record_323c78((uintptr_t)out,
        0x11223344u,0x55667788u,0x99aabbccu,0xddeeff00u)==12u);
    assert(writes==2u&&out[0]==0u&&out[6]==16u);
    return 0;
}
