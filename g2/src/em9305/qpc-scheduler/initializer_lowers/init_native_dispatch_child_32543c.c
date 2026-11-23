#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32543c..0x32544e: allocate a WSF event sized for the configured
 * payload length (config halfword at +0x2c) plus a 16-byte header. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);

uintptr_t opencfw_em9305_dispatch_child_32543c(void)
{
    uintptr_t config=em9305_ram_805c5c.u32_805cac;
    uint32_t length=*(volatile uint16_t *)(config+0x2cu);
    return opencfw_em9305_wsf_event_allocate((uint16_t)(length+16u));
}
