#include <stdint.h>

/* Native 0x32dbe4 and 0x32dd20: little-endian packet fields widened into
 * aligned output words.  The source reads remain in each native body's
 * instruction order so overlapping packet/output storage is observable. */
static uint8_t rd(uintptr_t p, unsigned n)
{ return *(volatile const uint8_t *)(p + n); }
static void wr16(uintptr_t p, unsigned n, uint16_t v)
{ *(volatile uint16_t *)(p + n) = v; }
static void wr32(uintptr_t p, unsigned n, uint32_t v)
{ *(volatile uint32_t *)(p + n) = v; }

uint32_t opencfw_em9305_packet_child_32dd20(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields = (uintptr_t)fields_word;
    uint8_t b2 = rd(payload, 2u), b3 = rd(payload, 3u), b1 = rd(payload, 1u);
    wr32(fields, 0u, (uint32_t)b1 | ((uint32_t)b2 << 8) | ((uint32_t)b3 << 16));
    uint8_t b5 = rd(payload, 5u), b6 = rd(payload, 6u), b4 = rd(payload, 4u);
    wr32(fields, 4u, (uint32_t)b4 | ((uint32_t)b5 << 8) | ((uint32_t)b6 << 16));
    uint8_t b8 = rd(payload, 8u), b7 = rd(payload, 7u);
    wr16(fields, 8u, (uint16_t)((uint16_t)b7 | ((uint16_t)b8 << 8)));
    return 9u;
}

uint32_t opencfw_em9305_packet_child_32dbe4(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields = (uintptr_t)fields_word;
    uint8_t b2 = rd(payload, 2u), b3 = rd(payload, 3u);
    uint8_t b1 = rd(payload, 1u), b4 = rd(payload, 4u);
    wr32(fields, 0u, (uint32_t)b1 | ((uint32_t)b2 << 8) |
                      ((uint32_t)b3 << 16) | ((uint32_t)b4 << 24));
    uint8_t b6 = rd(payload, 6u), b7 = rd(payload, 7u), b5 = rd(payload, 5u);
    wr32(fields, 4u, (uint32_t)b5 | ((uint32_t)b6 << 8) | ((uint32_t)b7 << 16));
    uint8_t b9 = rd(payload, 9u), b10 = rd(payload, 10u), b8 = rd(payload, 8u);
    wr32(fields, 8u, (uint32_t)b8 | ((uint32_t)b9 << 8) | ((uint32_t)b10 << 16));
    uint8_t b12 = rd(payload, 12u), b13 = rd(payload, 13u), b11 = rd(payload, 11u);
    wr32(fields, 12u, (uint32_t)b11 | ((uint32_t)b12 << 8) | ((uint32_t)b13 << 16));
    uint8_t b15 = rd(payload, 15u), b14 = rd(payload, 14u);
    wr16(fields, 16u, (uint16_t)((uint16_t)b14 | ((uint16_t)b15 << 8)));
    return 16u;
}
