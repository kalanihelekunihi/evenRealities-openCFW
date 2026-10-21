/* Native attsIsHashableAttr 0x534ea8; pinned Cordio atts_main.c. */
#include <stdint.h>
uint8_t audio_ble_atts_hash_skip_next; /* static bool at native RAM 0x20074f95 */
static const uint8_t *pointer_at(const uint8_t *p)
{
    uint32_t raw;
    __builtin_memcpy(&raw,p,4u);
    return (const uint8_t *)(uintptr_t)raw;
}
uint16_t attsIsHashableAttr(const uint8_t *attribute)
{
    if (audio_ble_atts_hash_skip_next) {
        audio_ble_atts_hash_skip_next=0u;
        return 0u;
    }
    const uint8_t *uuid_bytes=pointer_at(attribute);
    uint16_t uuid=(uint16_t)uuid_bytes[0]|((uint16_t)uuid_bytes[1]<<8u);
    uint16_t length=2u;
    if ((uint16_t)(uuid-0x2800u)<=2u || uuid==0x2803u || uuid==0x2900u) {
        if (uuid==0x2803u) audio_ble_atts_hash_skip_next=1u;
        const uint8_t *value_length=pointer_at(attribute+8u);
        length=(uint16_t)(length+((uint16_t)value_length[0]|
                                   ((uint16_t)value_length[1]<<8u)));
    } else if ((uint16_t)(uuid-0x2901u)>2u && uuid!=0x2905u) {
        return 0u;
    }
    return (uint16_t)(length+((attribute[0x0eu]&1u)?16u:2u));
}
