#include <stdint.h>

/* Native 0x32601c..0x32608a: PHY procedure response. A stored rejection
 * reason (+747) is sent as a reject and cleared. Otherwise send a 5-byte
 * 0x24 PDU: classified and raw signed level for the current PHY slot
 * (+332 indexed by PHY byte +766: min(phy,3), minus 1 unless phy is 4),
 * the transaction byte (+764) and 0xff; then mark the response sent
 * (+765). */
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_ll_signed_classify_31b374(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);

void opencfw_em9305_child_32601c(uintptr_t record)
{
    uint32_t reason=*(volatile uint8_t *)(record+747u);
    if(reason!=0u) {
        (void)opencfw_em9305_phy_reject_32698c(record,reason,1u);
        *(volatile uint8_t *)(record+747u)=0u;
        return;
    }
    uint32_t phy=*(volatile uint8_t *)(record+766u);
    uint32_t slot=(phy<3u?phy:3u)-(phy!=4u);
    int32_t level=*(volatile int8_t *)(record+slot+332u);
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(5u);
    if(packet!=0u) {
        *(volatile uint8_t *)packet=0x24u;
        *(volatile uint8_t *)(packet+1u)=
            (uint8_t)opencfw_em9305_ll_signed_classify_31b374((uint32_t)level);
        *(volatile uint8_t *)(packet+4u)=0xffu;
        *(volatile uint8_t *)(packet+2u)=*(volatile uint8_t *)(record+764u);
        *(volatile uint8_t *)(packet+3u)=(uint8_t)level;
        (void)opencfw_em9305_phy_packet_send_32d32c(record,packet);
    }
    *(volatile uint8_t *)(record+765u)=1u;
}
