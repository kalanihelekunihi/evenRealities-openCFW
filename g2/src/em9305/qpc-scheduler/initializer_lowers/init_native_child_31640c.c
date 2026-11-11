#include <stdint.h>

/* Native 0x31640c..0x31643a: if bit 1 of the record's mode byte (+544) is
 * set, run child 325c9c and start the PHY timer; otherwise report mode
 * event 0x1a and terminate reception with reason 0x6e. */
extern uint32_t opencfw_em9305_child_325c9c(uintptr_t record);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t record);
extern uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t context,uint32_t status);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t source,
                                                        uint32_t reason);

uint32_t opencfw_em9305_child_31640c(uintptr_t record)
{
    if((*(volatile uint8_t *)(record+544u)&2u)!=0u){
        (void)opencfw_em9305_child_325c9c(record);
        return opencfw_em9305_phy_timer_start_32c7e4(record);
    }
    (void)opencfw_em9305_mode_event_322fdc(record,0x1au);
    return opencfw_em9305_receive_terminate_325c08(record,0x6eu);
}
