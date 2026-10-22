/* Cordio ATTS indication/notification callback clearing, stock
 * 0x533934..0x5339ac; pinned Cordio atts_ind.c. */
#include <stdint.h>

extern void audio_ble_att_exec_callback_4b5074(uint8_t, uint8_t,
                                                uint16_t, uint8_t, uint16_t);

void audio_ble_atts_exec_callback_533934(uint8_t connection, uint16_t handle,
                                          uint8_t status)
{
    audio_ble_att_exec_callback_4b5074(connection, 0x12u, handle, status, 0u);
}

