#include <stdint.h>

/* Native 0x325c40..0x325c9c: send a 24-byte control PDU: opcode, the
 * 8-byte field from the source, one parameter byte, the record's two
 * bytes at +262 and twelve 0xff bytes. Returns 0 when no packet could be
 * allocated. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);

uint32_t opencfw_em9305_child_325c40(uintptr_t record,uint32_t opcode,uintptr_t source,
                                     uint32_t parameter)
{
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(0x18u);
    if(packet==0u) return 0u;
    volatile uint8_t *pdu=(volatile uint8_t *)packet;
    volatile uint8_t *in=(volatile uint8_t *)source;
    pdu[0]=(uint8_t)opcode;
    for(uint32_t i=0u;i<8u;++i) pdu[1u+i]=in[i];
    pdu[9]=(uint8_t)parameter;
    pdu[10]=*(volatile uint8_t *)(record+262u);
    pdu[11]=*(volatile uint8_t *)(record+263u);
    (void)opencfw_em9305_memset((void *)(packet+12u),0xffu,12u);
    return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
