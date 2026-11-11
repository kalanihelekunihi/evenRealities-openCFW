#include <stdint.h>

/* Native 0x326a2c..0x326a46: allocate a one-byte PHY packet, set its
 * opcode byte to 5 and send it for the record. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t record,
                                                     uintptr_t payload);

uint32_t opencfw_em9305_child_326a2c(uintptr_t record)
{
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(1u);
    if(packet==0u)return 0u;
    *(volatile uint8_t *)packet=5u;
    return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
