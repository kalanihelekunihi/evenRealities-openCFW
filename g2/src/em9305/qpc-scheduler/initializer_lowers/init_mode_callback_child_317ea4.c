#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x317ea4..0x317eba. ROM halfword configuration at 0x3357d0,
 * authenticated from em-inspection.bin offset 0x333d0 (base 0x302400):
 * 500,250,150,100,75,50,30,20. The caller passes the byte read at
 * ((uintptr_t)&em9305_ram_8027e0 + 0x3cu), not its context pointer. 0x303f5c reads a live config halfword. */
extern const uint16_t opencfw_em9305_init_secondary_intervals_3357d0[8];
uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t selector)
{
    if (selector>7u) selector=7u;
    uint32_t adjustment=opencfw_em9305_init_secondary_intervals_3357d0[selector];
    uintptr_t configuration=em9305_ram_805be0.u32_805c18;
    uint32_t base=*(volatile uint16_t *)configuration;
    return (uint16_t)(base+adjustment);
}
