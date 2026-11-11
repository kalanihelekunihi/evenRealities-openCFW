#include <stdint.h>

/* Native 0x3174d8..0x317508: if the head event of the queue at
 * object + 8 has the requested tag, remove it and return its payload
 * (event + 10); otherwise return 0. */
extern uintptr_t opencfw_em9305_wsf_event_peek(uintptr_t queue,uintptr_t out_u8);
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t out_u8);

uintptr_t opencfw_em9305_dispatch_child_3174d8(uintptr_t object,uint32_t tag)
{
    uintptr_t queue=object+8u;
    uint8_t found;
    if(opencfw_em9305_wsf_event_peek(queue,(uintptr_t)&found)==0u)return 0u;
    if(found!=tag)return 0u;
    return opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&found)+10u;
}
