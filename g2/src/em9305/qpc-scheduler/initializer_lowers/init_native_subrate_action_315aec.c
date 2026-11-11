#include <stdint.h>

/* Native 0x315aec..0x315bc6: start a connection subrate request. Without
 * local support (bit 5 of +548) or the host feature (bit 6 of 0x805a98)
 * report status 0xc; without the peer feature (bit 6 of +548) report
 * 0x1a. Otherwise mark +888, latch the requested parameters (+856..+864
 * and the handle +262, with the continuation number clamped below the
 * maximum) into +876..+887 and send LL_SUBRATE_REQ (0x27) with them,
 * setting bit 29 of +636; no PDU buffer terminates with 0x6f and reports
 * 0xd. Reports go through 323498 with the connection index. */
extern uint32_t opencfw_em9305_dispatch_child_323498(uint32_t handle, uint32_t status);
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t record, uintptr_t packet);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t record, uint32_t reason);

static uint32_t opencfw_em9305_subrate_index_315aec(uintptr_t record)
{
    uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    return (uint8_t)((int32_t)(record-base)/912);
}

void opencfw_em9305_subrate_action_315aec(uintptr_t record)
{
    uint32_t features=*(volatile uint32_t *)(record+548u);
    if((features&0x20u)==0u||(*(volatile uint8_t *)(uintptr_t)0x805a98u&0x40u)==0u){
        (void)opencfw_em9305_dispatch_child_323498(opencfw_em9305_subrate_index_315aec(record),0xcu);
        return;
    }
    if((features&0x40u)==0u){
        (void)opencfw_em9305_dispatch_child_323498(opencfw_em9305_subrate_index_315aec(record),0x1au);
        return;
    }
    *(volatile uint8_t *)(record+888u)=1u;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(0xbu);
    if(packet==0u){
        (void)opencfw_em9305_receive_terminate_325c08(record,0x6fu);
        (void)opencfw_em9305_dispatch_child_323498(opencfw_em9305_subrate_index_315aec(record),0xdu);
        return;
    }
    volatile uint8_t *p=(volatile uint8_t *)packet;
    volatile uint8_t *latched=(volatile uint8_t *)(record+876u);
    uint32_t handle=*(volatile uint16_t *)(record+262u);
    uint32_t factor_max=*(volatile uint16_t *)(record+856u);
    *(volatile uint16_t *)(record+878u)=(uint16_t)handle;
    uint32_t latency=*(volatile uint16_t *)(record+860u);
    uint32_t continuation=*(volatile uint16_t *)(record+862u);
    uint32_t timeout=*(volatile uint16_t *)(record+864u);
    *(volatile uint16_t *)(record+884u)=(uint16_t)latency;
    int32_t limit=(int32_t)factor_max-1;
    int32_t clamped=(int32_t)continuation<limit?(int32_t)continuation:limit;
    *(volatile uint16_t *)(record+876u)=(uint16_t)factor_max;
    *(volatile uint16_t *)(record+886u)=(uint16_t)timeout;
    *(volatile uint16_t *)(record+880u)=(uint16_t)clamped;
    p[0]=0x27u;
    p[1]=latched[0];
    p[2]=latched[1];
    p[3]=latched[2];
    p[4]=latched[3];
    p[5]=latched[8];
    p[6]=latched[9];
    p[7]=latched[4];
    p[8]=latched[5];
    p[9]=latched[10];
    p[10]=latched[11];
    (void)opencfw_em9305_phy_packet_send_32d32c(record,packet);
    *(volatile uint32_t *)(record+636u)|=1u<<29;
}
