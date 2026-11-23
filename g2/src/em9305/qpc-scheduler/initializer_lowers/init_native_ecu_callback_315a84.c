#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x315a84..0x315aec: send the 11-byte PHY packet 0x26 carrying the
 * record's 10 bytes at +856. When no packet is available, terminate
 * reception (reason 0x6f) and report status 0x0d for the connection
 * handle (record index in the 912-byte table at *((uintptr_t)&em9305_ram_805c5c + 0x14u)). */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t record,
                                                     uintptr_t payload);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t source,
                                                        uint32_t reason);
extern uint32_t opencfw_em9305_dispatch_child_323498(uint32_t handle,
                                                     uint32_t status);

uint32_t opencfw_em9305_ecu_callback_315a84(uintptr_t record)
{
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(11u);
    if(packet==0u){
        (void)opencfw_em9305_receive_terminate_325c08(record,0x6fu);
        uintptr_t base=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x14u);
        int32_t index=(int32_t)(record-base)/912;
        return opencfw_em9305_dispatch_child_323498((uint8_t)index,0x0du);
    }
    *(volatile uint8_t *)packet=0x26u;
    for(uint32_t i=0u;i<10u;++i)
        *(volatile uint8_t *)(packet+1u+i)=*(volatile uint8_t *)(record+856u+i);
    return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
