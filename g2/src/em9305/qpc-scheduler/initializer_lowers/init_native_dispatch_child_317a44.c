#include <stdint.h>

/* Native 0x317a44..0x317a82: decode a little-endian field block: bytes
 * 1..5 form a 40-bit value stored as a 64-bit word, bytes 6..7 a
 * halfword. Returns the consumed length, 8. */
uint32_t opencfw_em9305_dispatch_child_317a44(uintptr_t value_out, uintptr_t half_out,
                                              uintptr_t in)
{
    volatile const uint8_t *i=(volatile const uint8_t *)in;
    uint32_t half=i[6]+((uint32_t)i[7]<<8);
    uint32_t low=i[1]+((uint32_t)i[2]<<8)+((uint32_t)i[3]<<16)+((uint32_t)i[4]<<24);
    uint32_t high=i[5];
    *(volatile uint16_t *)half_out=(uint16_t)half;
    *(volatile uint32_t *)value_out=low;
    *(volatile uint32_t *)(value_out+4u)=high;
    return 8u;
}
