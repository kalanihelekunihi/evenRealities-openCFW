#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32db0c..0x32db52: decode the 16-bit PDU header at in[0..1]
 * into out[0..4]: LLID (bits 0..3), bits 5, 6 and 7, and the length byte
 * (masked to 6 bits when the configured version at +4 of ((uintptr_t)&em9305_ram_805c5c + 0x50u) is 8 or
 * below). Returns 2, the header length. */
uint32_t opencfw_em9305_dispatch_child_32db0c(uintptr_t out, uintptr_t in)
{
    volatile uint8_t *o=(volatile uint8_t *)out;
    uint32_t header=((uint32_t)*(volatile uint8_t *)(in+1u)<<8)+*(volatile uint8_t *)in;
    uintptr_t config=em9305_ram_805c5c.u32_805cac;
    o[0]=(uint8_t)(header&15u);
    uint32_t length=(header&0xff00u)>>8;
    if(*(volatile uint8_t *)(config+4u)<=8u)length&=63u;
    o[2]=(uint8_t)((header>>6)&1u);
    o[1]=(uint8_t)((header>>5)&1u);
    o[4]=(uint8_t)length;
    o[3]=(uint8_t)((header>>7)&1u);
    return 2u;
}

/* Same stock function 0x32db0c, also called under its child name. */
__typeof__(opencfw_em9305_dispatch_child_32db0c) opencfw_em9305_child_32db0c
    __attribute__((alias("opencfw_em9305_dispatch_child_32db0c")));
