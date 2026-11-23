#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x329fd8..0x32a000: look up the 912-byte table entry for the
 * packet's handle; if the entry is active, remember the packet in ((uintptr_t)&em9305_ram_805c5c + 0x10u)
 * and pass the entry and packet byte 3 to native 0x32a000. */
extern uint32_t opencfw_em9305_child_32a000(uint32_t entry, uint32_t code);

uint32_t opencfw_em9305_child_329fd8(uintptr_t packet)
{
    uint32_t handle = *(volatile uint16_t *)packet;
    uintptr_t entry = *(volatile uint32_t *)(uintptr_t)((uintptr_t)&em9305_ram_805c5c + 0x14u) + handle * 912u;
    if (*(volatile uint8_t *)entry == 0u) return (uint32_t)entry;
    em9305_ram_805c5c.u32_805c6c = (uint32_t)packet;
    return opencfw_em9305_child_32a000((uint32_t)entry, *(volatile uint8_t *)(packet + 3u));
}
