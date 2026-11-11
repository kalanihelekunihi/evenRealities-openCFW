#include <stdint.h>

/* Native 0x325324..0x325350: queue an LL event for the connection record
 * (handle = record index in the 912-byte table at *0x805c70) and count it
 * in the record's pending byte (+377). */
extern uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t queue,uint32_t handler,
                                                uintptr_t event);

void opencfw_em9305_child_325324(uintptr_t record,uintptr_t payload)
{
    uintptr_t base=*(volatile uint32_t *)0x805c70u;
    int32_t index=(int32_t)(record-base)/912;
    (void)opencfw_em9305_ll_event_enqueue(record+368u,(uint8_t)index,payload-2u);
    uint32_t pending=*(volatile uint8_t *)(record+377u);
    *(volatile uint8_t *)(record+377u)=(uint8_t)(pending+1u);
}
