/* Cordio HCI LE connection update command at stock Main 0x52af40. */
#include <stdint.h>

extern uint8_t *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint8_t);
extern void audio_ble_hci_cmd_send(void *);

void audio_ble_hci_conn_update_52af40(uint16_t handle,
                                      const uint8_t *connection_spec)
{
    uint8_t *command = audio_ble_hci_cmd_alloc_52ae38(0x2013u, 14u);
    if (command == 0)
        return;
    command[3] = (uint8_t)handle;
    command[4] = (uint8_t)(handle >> 8);
    for (uint32_t i = 0u; i < 12u; ++i)
        command[5u + i] = connection_spec[i];
    audio_ble_hci_cmd_send(command);
}
