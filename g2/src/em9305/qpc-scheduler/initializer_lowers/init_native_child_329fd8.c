#include <stdint.h>

/* Native 0x329fd8..0x32a000: look up the 912-byte table entry for the
 * packet's handle; if the entry is active, remember the packet in 0x805c6c
 * and pass the entry and packet byte 3 to native 0x32a000. */
extern uint32_t opencfw_em9305_child_32a000(uint32_t entry, uint32_t code);

uint32_t opencfw_em9305_child_329fd8(uintptr_t packet)
{
    uint32_t handle = *(volatile uint16_t *)packet;
    uintptr_t entry = *(volatile uint32_t *)(uintptr_t)0x805c70u + handle * 912u;
    if (*(volatile uint8_t *)entry == 0u) return (uint32_t)entry;
    *(volatile uint32_t *)(uintptr_t)0x805c6cu = (uint32_t)packet;
    return opencfw_em9305_child_32a000((uint32_t)entry, *(volatile uint8_t *)(packet + 3u));
}
