/* Cordio attcReqClear at stock Main 0x531af2. */
#include <stdint.h>

extern void audio_ble_attc_free_pkt_531ac0(uint8_t *);
extern void audio_ble_attc_exec_callback_531ad6(uint8_t, uint8_t, uint16_t, uint8_t);

void audio_ble_attc_req_clear_531af2(uint8_t connection, uint8_t *message,
                                     uint8_t status)
{
    audio_ble_attc_free_pkt_531ac0(message);
    const uint16_t handle =
        (uint16_t)message[8u] | ((uint16_t)message[9u] << 8);
    audio_ble_attc_exec_callback_531ad6(connection, message[2u], handle, status);
    message[2u] = 0u;
}
