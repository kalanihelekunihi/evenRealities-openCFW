#include <stdint.h>

/* Native 0x317a98..0x317ac0: unpack a little-endian 16-bit field word
 * into bytes: bits 0..1, bits 2..4, bit 5 and the high byte. Returns 2. */
uint32_t opencfw_em9305_dispatch_child_317a98(uintptr_t out,uintptr_t in)
{
    uint32_t value=*(volatile uint8_t *)in
                   +((uint32_t)*(volatile uint8_t *)(in+1u)<<8);
    volatile uint8_t *bytes=(volatile uint8_t *)out;
    bytes[3]=(uint8_t)(value>>8);
    bytes[0]=(uint8_t)(value&3u);
    bytes[2]=(uint8_t)((value>>5)&1u);
    bytes[1]=(uint8_t)((value>>2)&7u);
    return 2u;
}
