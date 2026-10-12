#include <assert.h>
#include <stdint.h>
#include <string.h>

uint32_t opencfw_em9305_init_transition_packet_check_32e278(uintptr_t);
static void set16(uint8_t *p,uint16_t v)
{p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u);}
static void set32(uint8_t *p,uint32_t v)
{for(unsigned i=0u;i<4u;i++)p[i]=(uint8_t)(v>>(i*8u));}
int main(void)
{
    uint8_t record[48];
    for(unsigned first=0u;first<4u;first++)
    for(unsigned second=0u;second<4u;second++)
    for(unsigned third=0u;third<3u;third++) {
        memset(record,0,sizeof record);
        set16(record+32u,first?0xffffu:0u);
        set16(record+40u,second?0xffffu:0u);
        record[38]=(uint8_t)(third==2u?9u:8u);
        set32(record+24u,1u);
        set16(record+36u,20u);
        record[42]=5u;
        uint32_t expect=(first!=0u&&second!=0u&&third!=2u);
        assert(opencfw_em9305_init_transition_packet_check_32e278(
            (uintptr_t)record)==expect);
        set32(record+28u,224u);
        assert(opencfw_em9305_init_transition_packet_check_32e278(
            (uintptr_t)record)==0u);
    }
    return 0;
}
