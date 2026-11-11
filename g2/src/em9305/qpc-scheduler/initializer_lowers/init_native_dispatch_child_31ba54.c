#include <stdint.h>

/* Native 0x31ba54..0x31ba78: when the queue selector byte is 0 or 1, pop
 * the next event from the queue at +4; other selectors return 0. */
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue, uintptr_t handler_out);

uintptr_t opencfw_em9305_dispatch_child_31ba54(uintptr_t queue_record)
{
    uint8_t handler;
    uint32_t selector=*(volatile uint8_t *)queue_record;
    if(selector>1u)return 0u;
    return opencfw_em9305_wsf_event_remove(queue_record+4u,(uintptr_t)&handler);
}
