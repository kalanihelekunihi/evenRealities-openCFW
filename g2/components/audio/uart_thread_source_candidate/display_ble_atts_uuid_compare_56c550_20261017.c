/* Cordio attsUuidCmp, stock 0x56c550..0x56c5aa. */
#include <stdint.h>

extern int memcmp(const void *, const void *, unsigned);
extern uint8_t attUuidCmp16to128(const uint8_t *, const uint8_t *);

uint8_t attsUuidCmp(uint8_t *attribute, uint8_t uuid_length,
                    const uint8_t *uuid)
{
    const uint8_t is_128 = (uint8_t)(attribute[0x0eu] & 1u);
    const uint8_t *const attribute_uuid = (const uint8_t *)(uintptr_t)
        *(const uint32_t *)(const void *)attribute;
    if ((!is_128 && uuid_length == 2u) ||
        (is_128 && uuid_length == 16u))
        return (uint8_t)(memcmp(attribute_uuid, uuid, uuid_length) == 0);
    if (!is_128 && uuid_length == 16u)
        return attUuidCmp16to128(attribute_uuid, uuid);
    return attUuidCmp16to128(uuid, attribute_uuid);
}
