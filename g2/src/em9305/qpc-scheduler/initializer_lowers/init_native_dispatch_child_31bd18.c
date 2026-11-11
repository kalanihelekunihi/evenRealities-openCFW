#include <stdint.h>

/* Native 0x31bd18..0x31bd46: unpack a descriptor. out[0..1] get bits 0
 * and 1 of in[0], out[2] = in[1]; when bit 0 is clear the 24-bit value
 * in[2..4] is stored as a word at out+4 and 5 is returned, else 2. */
uint32_t opencfw_em9305_dispatch_child_31bd18(uintptr_t out, uintptr_t in)
{
    volatile uint8_t *o=(volatile uint8_t *)out;
    volatile const uint8_t *i=(volatile const uint8_t *)in;
    uint32_t flags=i[0];
    o[0]=(uint8_t)(flags&1u);
    o[1]=(uint8_t)((flags>>1)&1u);
    o[2]=i[1];
    if((flags&1u)!=0u)return 2u;
    uint32_t value=((uint32_t)i[3]<<8)+i[2];
    value+=(uint32_t)i[4]<<16;
    *(volatile uint32_t *)(out+4u)=value;
    return 5u;
}
