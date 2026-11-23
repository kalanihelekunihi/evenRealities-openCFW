#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31a93c..0x31a97e: mark the record pending (+2 = 1). When the
 * role bit for the record (2 if its role byte +16 is 2, else 0) matches
 * the byte at ((uintptr_t)&em9305_ram_8019e8 + 0x11u), notify the scheduler with the record's +484 block
 * (if byte +241 is set) or +244 block; otherwise clear that bit in the
 * mask at ((uintptr_t)&em9305_ram_8019e8 + 0x10u) and run child 325edc with value 3. */
extern uint32_t opencfw_em9305_child_325edc(uintptr_t record,uint32_t value);
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t object);

uint32_t opencfw_em9305_child_31a93c(uintptr_t record)
{
    uint32_t bit=(*(volatile uint8_t *)(record+16u)==2u)?2u:0u;
    uint32_t current=*(volatile uint8_t *)((uintptr_t)&em9305_ram_8019e8 + 0x11u);
    *(volatile uint8_t *)(record+2u)=1u;
    if(bit!=current){
        uint32_t mask=*(volatile uint8_t *)((uintptr_t)&em9305_ram_8019e8 + 0x10u);
        *(volatile uint8_t *)((uintptr_t)&em9305_ram_8019e8 + 0x10u)=(uint8_t)(mask&~(1u<<bit));
        return opencfw_em9305_child_325edc(record,3u);
    }
    if(*(volatile uint8_t *)(record+241u)!=0u)
        return opencfw_em9305_ll_schedule_notify_313354(record+484u);
    return opencfw_em9305_ll_schedule_notify_313354(record+244u);
}
