/* Cordio HciDisconnectCmd 0x52af10: 0x0406, three payload bytes. */
#include <stdint.h>

extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint16_t);
extern void audio_ble_hci_cmd_send(void *);

void audio_ble_hci_disconnect_cmd_52af10(uint16_t handle, uint8_t reason)
{
    uint8_t *command = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x0406u, 3u);
    if (command == 0)
        return;
    command[3u] = (uint8_t)handle;
    command[4u] = (uint8_t)(handle >> 8u);
    command[5u] = reason;
    audio_ble_hci_cmd_send(command);
}
