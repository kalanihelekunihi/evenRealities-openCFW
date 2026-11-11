#include <stdint.h>

/* Native 0x325f9c..0x325fb6: allocate a one-byte PHY packet, set opcode
 * 10 and send it on the record; returns 0 when no packet is available. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);

uint32_t opencfw_em9305_child_325f9c(uintptr_t record)
{
    uintptr_t packet = opencfw_em9305_phy_packet_alloc_32d2f0(1u);
    if (packet == 0u) return 0u;
    *(volatile uint8_t *)packet = 10u;
    return opencfw_em9305_phy_packet_send_32d32c(record, packet);
}
