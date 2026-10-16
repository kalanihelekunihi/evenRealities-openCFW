#include <stdint.h>

/* Native 0x32e114 and 0x32e128.  R2 is live at the caller boundary but
 * unused by these two decoder bodies. */
static uint8_t packet_read(uintptr_t payload, unsigned offset)
{ return *(volatile const uint8_t *)(payload + offset); }
static void field_write8(uintptr_t fields, unsigned offset, uint8_t value)
{ *(volatile uint8_t *)(fields + offset) = value; }
static void field_write16(uintptr_t fields, unsigned offset, uint16_t value)
{ *(volatile uint16_t *)(fields + offset) = value; }

uint32_t opencfw_em9305_packet_child_32e114(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields = (uintptr_t)fields_word;
    uint8_t first = packet_read(payload, 1u);
    field_write8(fields, 0u, first);
    uint8_t second = packet_read(payload, 2u);
    field_write8(fields, 0u, (uint8_t)(first & 7u));
    field_write8(fields, 1u, (uint8_t)(second & 7u));
    return 3u;
}

uint32_t opencfw_em9305_packet_child_32e128(uint32_t fields_word,
                                               uintptr_t payload,
                                               uint32_t third)
{
    (void)third;
    uintptr_t fields = (uintptr_t)fields_word;
    field_write8(fields, 0u, packet_read(payload, 1u));
    field_write8(fields, 1u, packet_read(payload, 2u));
    uint8_t high = packet_read(payload, 4u);
    uint8_t low = packet_read(payload, 3u);
    field_write16(fields, 2u,
                  (uint16_t)((uint16_t)low | ((uint16_t)high << 8)));
    return 5u;
}
