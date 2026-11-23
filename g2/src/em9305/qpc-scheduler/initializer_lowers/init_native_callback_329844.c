#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x329844..0x329886: make the packet current (*((uintptr_t)&em9305_ram_805c5c + 0x10u)) and run
 * 329fd8 on it. A packet whose id byte (+2) is 255 is a broadcast: its
 * halfword index (+0) is stepped from 0 over every configured record
 * (config byte 34), running 329fd8 for each; returns the packet. */
extern uint32_t opencfw_em9305_child_329fd8(uintptr_t);

uint32_t opencfw_em9305_callback_329844(uintptr_t packet)
{
    volatile uint32_t *current=&em9305_ram_805c5c.u32_805c6c;
    if(*(volatile uint8_t *)(packet+2u)!=255u) {
        *current=packet;
        return opencfw_em9305_child_329fd8(packet);
    }
    uint32_t index=0u;
    for(;;) {
        *(volatile uint16_t *)packet=(uint16_t)index;
        uintptr_t config=em9305_ram_805c5c.u32_805cac;
        if((uint16_t)index>=*(volatile uint8_t *)(config+34u)) return (uint32_t)packet;
        *current=packet;
        (void)opencfw_em9305_child_329fd8(packet);
        index=*(volatile uint16_t *)packet+1u;
    }
}
