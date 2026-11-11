#include <stdint.h>

/* Native 0x3172dc..0x3172ec: tag the node header byte with bit 7 and
 * prepend the node to the record's queue at +184. */
extern uint32_t opencfw_em9305_wsf_queue_prepend(uintptr_t queue,uintptr_t node);

uint32_t opencfw_em9305_child_3172dc(uintptr_t record,uintptr_t payload,
                                     uint32_t flags)
{
    *(volatile uint8_t *)(payload-4u)=(uint8_t)(flags|0x80u);
    return opencfw_em9305_wsf_queue_prepend(record+184u,payload-8u);
}
