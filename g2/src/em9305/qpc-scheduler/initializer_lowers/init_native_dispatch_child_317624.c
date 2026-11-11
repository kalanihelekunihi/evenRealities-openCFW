#include <stdint.h>

/* Native 0x317624..0x317652: take the next event from the record's receive
 * queue (+0x30) when the queue is enabled (+108 nonzero) or the mode byte
 * (+44) is 0 or 1; otherwise return 0. */
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t,uintptr_t);

uintptr_t opencfw_em9305_dispatch_child_317624(uintptr_t record)
{
    uint8_t handler_id;
    if(*(volatile uint8_t *)(record+108u)==0u) {
        uint32_t mode=*(volatile uint8_t *)(record+44u);
        if(mode!=1u&&mode!=0u) return 0u;
    }
    return opencfw_em9305_wsf_event_remove(record+0x30u,(uintptr_t)&handler_id);
}
