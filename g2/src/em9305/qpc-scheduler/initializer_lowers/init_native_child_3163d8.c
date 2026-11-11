#include <stdint.h>

/* Native 0x3163d8..0x31640c: clear the 24-byte block at record + 684;
 * if bit 1 of the mode byte (+544) is set, run child 325c9c and start the
 * PHY timer, otherwise terminate reception with reason 0x71. */
extern void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t count);
extern uint32_t opencfw_em9305_child_325c9c(uintptr_t record);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t record);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t source,
                                                        uint32_t reason);

uint32_t opencfw_em9305_child_3163d8(uintptr_t record)
{
    (void)opencfw_em9305_memset((void *)(record+684u),0u,24u);
    if((*(volatile uint8_t *)(record+544u)&2u)!=0u){
        (void)opencfw_em9305_child_325c9c(record);
        return opencfw_em9305_phy_timer_start_32c7e4(record);
    }
    return opencfw_em9305_receive_terminate_325c08(record,0x71u);
}
