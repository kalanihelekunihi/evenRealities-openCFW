#include <stdint.h>

/* Native 0x32dba4.  MACU/MACDU build a 64-bit zero-extended accumulator
 * from the packet's low three bytes, ADD.F supplies byte four and ADC.F
 * propagates carry before the fifth byte enters the high word. */
static uint8_t rd(uintptr_t payload, unsigned offset)
{ return *(volatile const uint8_t *)(payload + offset); }
static void wr32(uintptr_t fields, unsigned offset, uint32_t value)
{ *(volatile uint32_t *)(fields + offset) = value; }
static void wr16(uintptr_t fields, unsigned offset, uint16_t value)
{ *(volatile uint16_t *)(fields + offset) = value; }

uint32_t opencfw_em9305_packet_child_32dba4(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields = (uintptr_t)fields_word;
    uint8_t b1 = rd(payload, 1u);
    uint8_t b2 = rd(payload, 2u);
    uint8_t b3 = rd(payload, 3u);
    uint8_t b4 = rd(payload, 4u);
    uint64_t accumulator = (uint64_t)b1 + ((uint64_t)b2 << 8u) +
                           ((uint64_t)b3 << 16u) + ((uint64_t)b4 << 24u);
    uint8_t b5 = rd(payload, 5u);
    wr32(fields, 0u, (uint32_t)accumulator);
    wr32(fields, 4u, (uint32_t)(accumulator >> 32u) + (uint32_t)b5);
    uint8_t b7 = rd(payload, 7u);
    uint8_t b6 = rd(payload, 6u);
    wr16(fields, 8u, (uint16_t)((uint16_t)b6 | ((uint16_t)b7 << 8u)));
    return 8u;
}
