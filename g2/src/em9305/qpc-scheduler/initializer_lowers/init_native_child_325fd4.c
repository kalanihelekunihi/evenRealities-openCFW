#include <stdint.h>

/* Native 0x325fd4..0x32601a: send a 4-byte PHY packet 0x23 carrying the
 * PHY bit for the record's mode byte (+766), the byte +764 and the table
 * byte at record + 332 + min(mode,3) - (mode != 4). */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t record,
                                                     uintptr_t payload);

uint32_t opencfw_em9305_child_325fd4(uintptr_t record)
{
    uint32_t mode=*(volatile uint8_t *)(record+766u);
    uint32_t value=*(volatile uint8_t *)(record+764u);
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(4u);
    if(packet==0u)return 0u;
    *(volatile uint8_t *)packet=0x23u;
    uint32_t slot=(mode<3u?mode:3u)-(mode!=4u?1u:0u);
    uint32_t current=*(volatile uint8_t *)(record+766u);
    *(volatile uint8_t *)(packet+2u)=(uint8_t)value;
    *(volatile uint8_t *)(packet+1u)=(uint8_t)(1u<<((current-1u)&31u));
    *(volatile uint8_t *)(packet+3u)=*(volatile uint8_t *)(record+332u+slot);
    return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
