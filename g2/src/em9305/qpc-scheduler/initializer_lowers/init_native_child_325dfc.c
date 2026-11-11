#include <stdint.h>

/* Native 0x325dfc..0x325e4c: send a 23-byte PHY packet with opcode 3:
 * the record's 8 bytes at +445, bytes +454/+455, 8 bytes at +421 and
 * 4 bytes at +437. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t record,
                                                     uintptr_t payload);

uint32_t opencfw_em9305_child_325dfc(uintptr_t record)
{
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(23u);
    if(packet==0u)return 0u;
    *(volatile uint8_t *)packet=3u;
    (void)opencfw_em9305_memcpy((void *)(packet+1u),(const void *)(record+445u),8u);
    *(volatile uint8_t *)(packet+9u)=*(volatile uint8_t *)(record+454u);
    *(volatile uint8_t *)(packet+10u)=*(volatile uint8_t *)(record+455u);
    (void)opencfw_em9305_memcpy((void *)(packet+11u),(const void *)(record+421u),8u);
    (void)opencfw_em9305_memcpy((void *)(packet+19u),(const void *)(record+437u),4u);
    return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
