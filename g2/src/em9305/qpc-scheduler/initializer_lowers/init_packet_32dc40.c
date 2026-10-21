#include <stdint.h>

/* Native 0x32dc40.  Mask widths are BMSK bit indices plus one.  This
 * decoder writes through output offset 0x31 but returns native length 0x24. */
static uint8_t rd(uintptr_t p, unsigned n)
{ return *(volatile const uint8_t *)(p + n); }
static void w8(uintptr_t p, unsigned n, uint8_t v)
{ *(volatile uint8_t *)(p + n) = v; }
static void w16(uintptr_t p, unsigned n, uint16_t v)
{ *(volatile uint16_t *)(p + n) = v; }
static void w32(uintptr_t p, unsigned n, uint32_t v)
{ *(volatile uint32_t *)(p + n) = v; }

uint32_t opencfw_em9305_packet_child_32dc40(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t f = (uintptr_t)fields_word;
    for (unsigned i = 0; i < 4; ++i) w8(f, i, rd(payload, i + 1u));
    uint8_t b6 = rd(payload, 6u), b5 = rd(payload, 5u);
    uint16_t word = (uint16_t)((uint16_t)b5 | ((uint16_t)b6 << 8));
    w16(f, 6u, (uint16_t)(word & 0x0fffu));
    w8(f, 4u, (uint8_t)((word >> 15) & 1u));
    uint8_t b8 = rd(payload, 8u), b7 = rd(payload, 7u);
    w16(f, 8u, (uint16_t)(((uint16_t)b7 | ((uint16_t)b8 << 8)) & 0x0fffu));
    uint8_t b10 = rd(payload, 10u), b11 = rd(payload, 11u), b9 = rd(payload, 9u);
    w32(f, 12u, ((uint32_t)b9 | ((uint32_t)b10 << 8) |
                    ((uint32_t)b11 << 16)) & 0x000fffffu);
    uint8_t b13 = rd(payload, 13u), b14 = rd(payload, 14u), b12 = rd(payload, 12u);
    w32(f, 16u, ((uint32_t)b12 | ((uint32_t)b13 << 8) |
                    ((uint32_t)b14 << 16)) & 0x000fffffu);
    uint8_t b16 = rd(payload, 16u), b15 = rd(payload, 15u);
    w16(f, 20u, (uint16_t)((uint16_t)b15 | ((uint16_t)b16 << 8)));
    uint8_t b18 = rd(payload, 18u), b17 = rd(payload, 17u);
    w16(f, 22u, (uint16_t)((uint16_t)b17 | ((uint16_t)b18 << 8)));
    w8(f, 24u, rd(payload, 19u));
    uint8_t b21 = rd(payload, 21u), b22 = rd(payload, 22u), b20 = rd(payload, 20u);
    w32(f, 28u, (uint32_t)b20 | ((uint32_t)b21 << 8) | ((uint32_t)b22 << 16));
    uint8_t b23 = rd(payload, 23u);
    w8(f, 32u, (uint8_t)(b23 & 15u));
    w8(f, 33u, (uint8_t)(b23 >> 4));
    w8(f, 34u, rd(payload, 24u));
    w8(f, 35u, rd(payload, 25u));
    uint8_t b27 = rd(payload, 27u), b26 = rd(payload, 26u);
    w16(f, 36u, (uint16_t)((uint16_t)b26 | ((uint16_t)b27 << 8)));
    uint8_t b29 = rd(payload, 29u), b30 = rd(payload, 30u), b28 = rd(payload, 28u);
    w32(f, 40u, (uint32_t)b28 | ((uint32_t)b29 << 8) | ((uint32_t)b30 << 16));
    uint8_t b32 = rd(payload, 32u), b33 = rd(payload, 33u), b31 = rd(payload, 31u);
    w32(f, 44u, (uint32_t)b31 | ((uint32_t)b32 << 8) | ((uint32_t)b33 << 16));
    uint8_t b35 = rd(payload, 35u), b34 = rd(payload, 34u);
    w16(f, 48u, (uint16_t)((uint16_t)b34 | ((uint16_t)b35 << 8)));
    return 36u;
}
