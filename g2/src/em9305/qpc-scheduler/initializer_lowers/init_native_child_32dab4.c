#include <stdint.h>

/* Native 0x32dab4..0x32dae2: copy an 8-byte little-endian field from the
 * source into out+4 (one 32-bit word) and out+8..11 (four bytes);
 * returns the 8 bytes consumed. */
uint32_t opencfw_em9305_child_32dab4(uintptr_t out,uintptr_t source)
{
    volatile uint8_t *in=(volatile uint8_t *)source;
    volatile uint8_t *field=(volatile uint8_t *)out;
    uint32_t word=in[0]+((uint32_t)in[1]<<8)+((uint32_t)in[2]<<16)+((uint32_t)in[3]<<24);
    *(volatile uint32_t *)(out+4u)=word;
    field[8]=in[4];
    field[9]=in[5];
    field[10]=in[6];
    field[11]=in[7];
    return 8u;
}
