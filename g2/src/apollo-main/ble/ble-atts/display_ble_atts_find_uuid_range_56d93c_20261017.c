/* Cordio attsFindUuidInRange, stock 0x56d93c..0x56d9ec. */
#include <stdint.h>

extern uint8_t audio_ble_atts_state[];
extern uint8_t attsUuidCmp(uint8_t *attribute, uint8_t uuid_length,
                           const uint8_t *uuid);

uint16_t attsFindUuidInRange(uint16_t start, uint16_t end,
                             uint8_t uuid_length, const uint8_t *uuid,
                             void **attribute_out, void **group_out)
{
    uint8_t *group = (uint8_t *)(uintptr_t)
        *(const uint32_t *)(const void *)(audio_ble_atts_state + 0x258u);
    while (group != 0) {
        const uint16_t first = *(const uint16_t *)(const void *)(group + 0x10u);
        const uint16_t last = *(const uint16_t *)(const void *)(group + 0x12u);
        if (start < first && end >= first)
            start = first;
        if (start >= first && start <= last) {
            uint8_t *attribute = (uint8_t *)(uintptr_t)
                *(const uint32_t *)(const void *)(group + 4u);
            attribute += (uint32_t)(start - first) * 0x10u;
            *attribute_out = attribute;
            while (start <= last && start <= end) {
                if (attsUuidCmp(attribute, uuid_length, uuid) != 0u) {
                    *group_out = group;
                    return start;
                }
                if (start == 0xffffu)
                    break;
                ++start;
                attribute += 0x10u;
                *attribute_out = attribute;
            }
        }
        group = (uint8_t *)(uintptr_t)*(const uint32_t *)(const void *)group;
    }
    return 0u;
}
