#include <stdint.h>

/* Native 0x325e4c..0x325e84: send a 13-byte PHY packet with opcode 4,
 * the record's 8 bytes at +429 and 4 bytes at +441. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t record,
                                                     uintptr_t payload);

uint32_t opencfw_em9305_child_325e4c(uintptr_t record)
{
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(13u);
    if(packet==0u)return 0u;
    *(volatile uint8_t *)packet=4u;
    (void)opencfw_em9305_memcpy((void *)(packet+1u),(const void *)(record+429u),8u);
    (void)opencfw_em9305_memcpy((void *)(packet+9u),(const void *)(record+441u),4u);
    return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
