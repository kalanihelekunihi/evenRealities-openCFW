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

void audio_ble_atts_ind_ntf_callback_53394c(uint8_t connection,
                                              void *ccb_arg, uint8_t status)
{
    uint8_t *const ccb = (uint8_t *)ccb_arg;
    uint16_t *const pending_ind = (uint16_t *)(void *)(ccb + 0x28u);
    if (*pending_ind != 0u) {
        audio_ble_atts_exec_callback_533934(connection, *pending_ind, status);
        *pending_ind = 0u;
    }
    for (uint32_t index = 0u; index < 10u; ++index) {
        uint16_t *const pending =
            (uint16_t *)(void *)(ccb + 0x2au + index * 2u);
        if (*pending != 0u) {
            audio_ble_atts_exec_callback_533934(connection, *pending, status);
            *pending = 0u;
        }
    }
}
