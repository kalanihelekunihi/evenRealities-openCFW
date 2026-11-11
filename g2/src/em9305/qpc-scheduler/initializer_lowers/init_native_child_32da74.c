#include <stdint.h>

/* Native 0x32da74..0x32dab2: unpack a 7-byte field (channel map / instant
 * style): bytes 0..4 little-endian into the 64-bit word at out+4/out+8
 * (the stock code builds it in the MAC accumulator), bytes 5..6
 * little-endian into the halfword at out+12. Returns the consumed length
 * 7. Bytes are read in stock order relative to the stores. */
uint32_t opencfw_em9305_child_32da74(uintptr_t out, uintptr_t data)
{
    const volatile uint8_t *in = (const volatile uint8_t *)data;
    uint32_t low = (uint32_t)in[0] | ((uint32_t)in[1] << 8) | ((uint32_t)in[2] << 16) |
                   ((uint32_t)in[3] << 24);
    uint32_t high = in[4];
    *(volatile uint32_t *)(out + 4u) = low;
    *(volatile uint32_t *)(out + 8u) = high;
    uint32_t tail = ((uint32_t)in[6] << 8) | in[5];
    *(volatile uint16_t *)(out + 12u) = (uint16_t)tail;
    return 7u;
}
