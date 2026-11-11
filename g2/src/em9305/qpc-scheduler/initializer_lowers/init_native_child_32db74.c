#include <stdint.h>

/* Native 0x32db74..0x32dba4: unpack a 3-byte packed header into fields:
 * out[0]=bits 0-5, out[1]=bit 6, out[2]=bit 7 of byte 0; the little-endian
 * halfword at bytes 1-2 gives out+4 (low 13 bits) and out[6] (top 3 bits).
 * Byte 0 is re-read for each field, as stock does. */
void opencfw_em9305_child_32db74(uintptr_t out,uintptr_t packed)
{
    volatile uint8_t *source=(volatile uint8_t *)packed;
    volatile uint8_t *field=(volatile uint8_t *)out;
    field[0]=(uint8_t)(source[0]&0x3fu);
    field[1]=(uint8_t)((source[0]>>6)&1u);
    field[2]=(uint8_t)(source[0]>>7);
    uint32_t word=((uint32_t)source[2]<<8)+source[1];
    *(volatile uint16_t *)(out+4u)=(uint16_t)(word&0x1fffu);
    field[6]=(uint8_t)((word&0xe000u)>>13);
}
