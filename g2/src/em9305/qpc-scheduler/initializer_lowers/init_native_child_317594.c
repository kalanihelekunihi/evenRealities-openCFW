#include <stdint.h>

/* Native 0x317594..0x3175bc: build an 8-byte record: byte 0 cleared,
 * bytes 1..4 the little-endian word, byte 5 the type byte, bytes 6..7 the
 * little-endian halfword. Returns the record length 8. */
uint32_t opencfw_em9305_child_317594(uintptr_t out,uint32_t word,
                                     uint32_t type,uint32_t half)
{
    volatile uint8_t *bytes=(volatile uint8_t *)out;
    bytes[6]=(uint8_t)half;
    bytes[5]=(uint8_t)type;
    bytes[1]=(uint8_t)word;
    bytes[7]=(uint8_t)(half>>8);
    bytes[4]=(uint8_t)(word>>24);
    bytes[3]=(uint8_t)(word>>16);
    bytes[2]=(uint8_t)(word>>8);
    bytes[0]=0u;
    return 8u;
}
