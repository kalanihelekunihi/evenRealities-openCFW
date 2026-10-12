#include <stdint.h>

/* Native 0x32de6c, 0x32deac and 0x32e1f4.  The third incoming register is
 * unused by these three bodies, but retained in the connected caller ABI. */
static uint8_t packet_byte(uintptr_t payload, unsigned offset)
{ return *(volatile const uint8_t *)(payload + offset); }
static void field_byte(uintptr_t fields, unsigned offset, uint8_t value)
{ *(volatile uint8_t *)(fields + offset) = value; }
static void field_halfword(uintptr_t fields, unsigned offset, uint16_t value)
{ *(volatile uint16_t *)(fields + offset) = value; }

uint32_t opencfw_em9305_packet_child_32de6c(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields = (uintptr_t)fields_word;
    field_byte(fields, 0u, packet_byte(payload, 1u));
    for (unsigned pair = 0u; pair < 5u; ++pair) {
        uint8_t high = packet_byte(payload, 3u + 2u * pair);
        uint8_t low = packet_byte(payload, 2u + 2u * pair);
        field_halfword(fields, 2u + 2u * pair,
                       (uint16_t)((uint16_t)low | ((uint16_t)high << 8)));
    }
    return 12u;
}

uint32_t opencfw_em9305_packet_child_32deac(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields = (uintptr_t)fields_word;
    for (unsigned pair = 0u; pair < 4u; ++pair) {
        uint8_t high = packet_byte(payload, 2u + 2u * pair);
        uint8_t low = packet_byte(payload, 1u + 2u * pair);
        field_halfword(fields, 2u * pair,
                       (uint16_t)((uint16_t)low | ((uint16_t)high << 8)));
    }
    return 9u;
}

uint32_t opencfw_em9305_packet_child_32e1f4(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields = (uintptr_t)fields_word;
    field_byte(fields, 0u, packet_byte(payload, 1u));
    uint8_t high = packet_byte(payload, 3u);
    uint8_t low = packet_byte(payload, 2u);
    field_halfword(fields, 2u, (uint16_t)((uint16_t)low | ((uint16_t)high << 8)));
    high = packet_byte(payload, 5u);
    low = packet_byte(payload, 4u);
    field_halfword(fields, 4u, (uint16_t)((uint16_t)low | ((uint16_t)high << 8)));
    return 6u;
}
