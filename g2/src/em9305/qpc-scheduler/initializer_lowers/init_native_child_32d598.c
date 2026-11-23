#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32d598..0x32d5aa: allocate a WSF event sized for the configured
 * payload length (config halfword +0x2c) plus a 16-byte header. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);

uintptr_t opencfw_em9305_child_32d598(void)
{
    uintptr_t config = em9305_ram_805c5c.u32_805cac;
    uint16_t length = (uint16_t)(*(volatile uint16_t *)(config + 0x2cu) + 0x10u);
    return opencfw_em9305_wsf_event_allocate(length);
}
