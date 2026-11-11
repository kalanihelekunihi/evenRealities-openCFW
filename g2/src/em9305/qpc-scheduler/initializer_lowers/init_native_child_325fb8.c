#include <stdint.h>

/* Native 0x325fb8..0x325fd2: allocate a one-byte PHY packet, tag it with
 * opcode 11 and send it on the record. Returns 0 if allocation failed. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);

uint32_t opencfw_em9305_child_325fb8(uintptr_t record)
{
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(1u);
    if(packet==0u) return 0u;
    *(volatile uint8_t *)packet=11u;
    return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
