#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x325ccc..0x325d50: start the connection-update receive window.
 * Marks +672, copies +664/+666 to +678/+680, aligns the window offset
 * (+692 x 1250 us) through 31340c and asks 3136fc for an anchor with the
 * interval bounds (+660/+662 x 1250) and latency (+592). On success sets
 * +192 and stores the anchor scaled by 0x1a36e3 / 2^31 at +676; on failure
 * terminates the receive with reason 0x72. */
extern uint32_t opencfw_em9305_child_31340c(uint32_t offset);
extern uint32_t opencfw_em9305_child_3136fc(uint32_t handle, uint32_t minimum,
                                            uint32_t maximum, uint32_t offset,
                                            uint32_t latency, uintptr_t anchor_out);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t record, uint32_t reason);

uint32_t opencfw_em9305_child_325ccc(uintptr_t record)
{
    uint32_t anchor;
    uint32_t window=*(volatile uint8_t *)(record+692u);
    uint32_t first=*(volatile uint16_t *)(record+664u);
    uint32_t second=*(volatile uint16_t *)(record+666u);
    uint32_t latency=*(volatile uint16_t *)(record+592u);
    uint32_t maximum=*(volatile uint16_t *)(record+662u);
    uint32_t minimum=*(volatile uint16_t *)(record+660u);
    *(volatile uint8_t *)(record+672u)=1u;
    *(volatile uint16_t *)(record+678u)=(uint16_t)first;
    *(volatile uint16_t *)(record+680u)=(uint16_t)second;
    uint32_t offset=opencfw_em9305_child_31340c(window*1250u);
    uintptr_t base=em9305_ram_805c5c.u32_805c70;
    uint32_t handle=(uint8_t)((int32_t)(record-base)/912);
    if(opencfw_em9305_child_3136fc(handle,minimum*1250u,maximum*1250u,offset,latency,
                                   (uintptr_t)&anchor)==0u)
        return opencfw_em9305_receive_terminate_325c08(record,0x72u);
    *(volatile uint8_t *)(record+192u)=1u;
    uint32_t scaled=(uint32_t)(((uint64_t)anchor*0x1a36e3u)>>31);
    *(volatile uint16_t *)(record+676u)=(uint16_t)scaled;
    return scaled;
}
