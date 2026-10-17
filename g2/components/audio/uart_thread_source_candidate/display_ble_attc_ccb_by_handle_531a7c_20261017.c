/* Cordio attcCcbByHandle at stock Main 0x531a7c. */
#include <stdint.h>

extern uint8_t audio_ble_attc_state[];
extern uint8_t DmConnIdByHandle(uint16_t);

uint8_t *audio_ble_attc_ccb_by_handle_531a7c(uint16_t handle,
                                               uint8_t slot)
{
    uint8_t connection = DmConnIdByHandle(handle);
    if (connection == 0u)
        return 0;
    return audio_ble_attc_state + ((uint32_t)connection - 1u) * 0x84u +
           (uint32_t)slot * 0x2cu;
}
