#include <stdint.h>

/* Native 0x325350..0x325374: remove one event from the queue at 0x805abc;
 * on success store its one-byte tag as a halfword at the output and
 * return the event payload (event + 2), otherwise 0. */
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t out_u8);

uintptr_t opencfw_em9305_child_325350(uintptr_t out)
{
    uint8_t tag;
    uintptr_t event=opencfw_em9305_wsf_event_remove(0x805abcu,(uintptr_t)&tag);
    if(event==0u)return 0u;
    *(volatile uint16_t *)out=tag;
    return event+2u;
}
