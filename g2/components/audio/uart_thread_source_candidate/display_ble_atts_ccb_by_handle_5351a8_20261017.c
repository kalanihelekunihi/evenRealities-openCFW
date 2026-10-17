/* Cordio attsCcbByHandle; stock Main 0x5351a8. */
#include <stdint.h>
extern uint8_t DmConnIdByHandle(uint16_t);
extern uint8_t audio_ble_atts_state[];
uint8_t *audio_ble_atts_ccb_by_handle_5351a8(uint16_t handle, uint8_t slot)
{
    const uint8_t connection = DmConnIdByHandle(handle);
    if (connection == 0u) return 0;
    return audio_ble_atts_state + ((uint32_t)connection - 1u) * 0xc0u +
           (uint32_t)slot * 0x40u;
}
