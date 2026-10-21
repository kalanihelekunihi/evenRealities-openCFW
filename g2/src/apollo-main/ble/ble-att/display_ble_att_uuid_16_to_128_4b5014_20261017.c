/* Cordio attUuidCmp16to128, stock 0x4b5014..0x4b5036. */
#include <stdint.h>

extern uint8_t audio_ble_att_uuid_base_2000044c[16];
extern int memcmp(const void *, const void *, unsigned);

uint8_t attUuidCmp16to128(const uint8_t *uuid16, const uint8_t *uuid128)
{
    audio_ble_att_uuid_base_2000044c[12] = uuid16[0];
    audio_ble_att_uuid_base_2000044c[13] = uuid16[1];
    return (uint8_t)(memcmp(audio_ble_att_uuid_base_2000044c,
                            uuid128, 16u) == 0);
}
