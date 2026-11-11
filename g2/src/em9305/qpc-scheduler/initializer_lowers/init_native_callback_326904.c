#include <stdint.h>

/* Native 0x326904..0x32698c: send the 5-byte 0x25 power-change PDU for a
 * PHY (1-based bit index) once the record's response is out (+765): PHY
 * mask, classified and raw signed level, and the delta byte. For the
 * coded PHY (mask 4) with a pending update, the flags become 0x0c when the
 * stored levels (+334/+335) agree; when they differ a second PDU is sent
 * with flags 8 and the stored level (+335). Returns 0 if nothing was
 * sent. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_ll_signed_classify_31b374(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);

uint32_t opencfw_em9305_callback_326904(uintptr_t record,uint32_t phy,uint32_t delta,
                                        uint32_t level,uint32_t pending)
{
    if(*(volatile uint8_t *)(record+765u)==0u) return 0u;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(5u);
    if(packet==0u) return 0u;
    volatile uint8_t *pdu=(volatile uint8_t *)packet;
    volatile uint8_t *stored=(volatile uint8_t *)(record+334u);
    uint32_t flags=1u<<((phy-1u)&31u);
    uint32_t differ=0u;
    if((uint8_t)flags==4u&&pending!=0u) {
        uint32_t first=stored[0];
        uint32_t second=stored[1];
        differ=second!=first;
        if(!differ) flags=0x0cu;
    }
    pdu[0]=0x25u;
    pdu[1]=(uint8_t)flags;
    pdu[2]=(uint8_t)opencfw_em9305_ll_signed_classify_31b374(level);
    pdu[4]=(uint8_t)level;
    pdu[3]=(uint8_t)delta;
    uint32_t status=opencfw_em9305_phy_packet_send_32d32c(record,packet);
    if(differ==0u) return status;
    int32_t current=*(volatile int8_t *)(record+335u);
    pdu[1]=8u;
    pdu[2]=(uint8_t)opencfw_em9305_ll_signed_classify_31b374((uint32_t)current);
    pdu[4]=(uint8_t)current;
    pdu[3]=(uint8_t)delta;
    return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
