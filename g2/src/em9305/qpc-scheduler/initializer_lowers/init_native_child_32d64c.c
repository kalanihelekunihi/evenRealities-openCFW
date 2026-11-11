#include <stdint.h>

/* Native 0x32d64c..0x32d692: sum the transmit time of every event queued
 * on the record (+360): one unit for a padding entry (tag 255), otherwise
 * the record timing of the event length (+4) at the record's packet mode.
 * Returns the low byte of the sum. Stock reads the length into R12 before
 * calling 32d4b0, which does not touch R12. */
extern uintptr_t opencfw_em9305_wsf_event_at(uintptr_t queue,uint32_t index,
                                             uintptr_t out_u8);
extern uint32_t opencfw_em9305_ll_event_mode_32d4b0(uintptr_t record);
extern uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t length,
                                                          uint32_t unit);

uint32_t opencfw_em9305_child_32d64c(uintptr_t record)
{
    uint32_t total=0u;
    for(uint32_t index=0u;;++index){
        uint8_t tag;
        uintptr_t event=opencfw_em9305_wsf_event_at(record+360u,(uint8_t)index,
                                                    (uintptr_t)&tag);
        if(event==0u)return (uint8_t)total;
        if(tag==255u){
            total+=1u;
            continue;
        }
        uint32_t length=*(volatile uint16_t *)(event+4u);
        uint32_t mode=opencfw_em9305_ll_event_mode_32d4b0(record);
        total+=opencfw_em9305_radio_record_timing_30c40c(length,mode);
    }
}
