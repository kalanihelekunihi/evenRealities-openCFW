#include <stdint.h>

/* Native 0x317ea4..0x317eba. ROM halfword configuration at 0x3357d0,
 * authenticated from em-inspection.bin offset 0x333d0 (base 0x302400):
 * 500,250,150,100,75,50,30,20. The caller passes the byte read at
 * 0x80281c, not its context pointer. 0x303f5c reads a live config halfword. */
static const uint16_t interval_adjustment[8]={500u,250u,150u,100u,
                                               75u,50u,30u,20u};
uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t selector)
{
    if (selector>7u) selector=7u;
    uint32_t adjustment=interval_adjustment[selector];
    uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805c18u;
    uint32_t base=*(volatile uint16_t *)configuration;
    return (uint16_t)(base+adjustment);
}
